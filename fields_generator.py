from xml.dom.minidom import parse
from svg.path import parse_path, Line, CubicBezier, Move
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union, cascaded_union
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle
import datetime
from random import choice, uniform
from PIL import Image

def svg_file_to_polygon(svg_file, num_points=20, plot=False, mirror=False):
    dom = parse(svg_file)
    path_strings = [path.getAttribute('d') for path in dom.getElementsByTagName('path')]
    
    polygons = []
    for path_string in path_strings:
        path = parse_path(path_string)
        points = []
        for command in path:
            if isinstance(command, Line) or isinstance(command, CubicBezier):
                if isinstance(command, Line):
                    points.append((command.end.real, -command.end.imag if mirror else command.end.imag))
                else:  # CubicBezier
                    for t in np.linspace(0, 1, num=num_points):
                        point = command.point(t)
                        points.append((point.real, -point.imag if mirror else point.imag))
            elif isinstance(command, Move):
                if points and len(points) >= 4:  # Ensure there are at least 4 points
                    polygons.append(Polygon(points))
                    points = []  # Start a new polygon
                points.append((command.start.real, -command.start.imag if mirror else command.start.imag))

        if points and len(points) >= 4:  # Add the last polygon if it has at least 4 points
            polygons.append(Polygon(points))

    # Create a MultiPolygon from all the polygons
    multi_polygon = MultiPolygon(polygons)

    # Plot the polygons if requested
    if plot:
        fig, ax = plt.subplots()
        if isinstance(multi_polygon, MultiPolygon):
            for polygon in multi_polygon.geoms:
                x, y = polygon.exterior.xy
                ax.plot(x, y)
        elif isinstance(multi_polygon, Polygon):
            x, y = multi_polygon.exterior.xy
            ax.plot(x, y)
        plt.show()

    return multi_polygon

def generate_points(polygon, num_points=100, mode='random', debug=False, theta=None):
    minx, miny, maxx, maxy = polygon.bounds
    points = []

    if mode == 'random':
        while len(points) < num_points:
            pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
            if polygon.contains(pnt):
                points.append((pnt.x, pnt.y))  # Append as tuple
    
    elif mode == 'grid':
        # Define the number of points in the x and y directions
        nx, ny = (5, 10)
        x = np.linspace(minx, maxx, nx)
        y = np.linspace(miny, maxy, ny)
    
        # Generate points with a smaller random offset for each coordinate
        points = [(xi + (np.random.rand() - 0.01) * (maxx - minx) / (nx * 4), 
                   yi + (np.random.rand() - 0.5) * (maxy - miny) / (ny * 4)) 
                  for xi in x for yi in y]
            
        # If theta is not provided, generate a random rotation angle
        if theta is None:
            theta = np.random.rand() * 2 * np.pi

        # Rotation matrix
        rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                    [np.sin(theta), np.cos(theta)]])
    
        # Calculate the center of the polygon
        center = [polygon.centroid.x, polygon.centroid.y]
        
        # Apply rotation to each point around the center of the polygon
        points = [np.dot(rotation_matrix, np.subtract(point, center)) + center for point in points]
    
        # Filter out the points that are not within the polygon after rotation
        # points = [point for point in points if polygon.contains(Point(point))]
        
    else:
        raise ValueError(f"Invalid mode: {mode}")

    if debug:
        fig, ax = plt.subplots()
        if isinstance(polygon, MultiPolygon):
            for poly in polygon.geoms:
                ax.plot(*poly.exterior.xy, 'k-')
        else:
            ax.plot(*polygon.exterior.xy, 'k-')
        if points:  # Check if points is not empty
            ax.scatter(*zip(*points), color='b', s=5)  # Smaller points
        plt.show()

    return np.array(points)

def fill_polygon_with_voronoi(polygon, points, plot=False, debug=False, keep_outline=True):
    
    # Initialize ax
    fig, ax = plt.subplots()
    
    # Convert points to a 2-D array
    points_array = np.array(points)
 
    # Create the Voronoi diagram
    vor = Voronoi(points_array)

    # Create polygons for each Voronoi region
    voronoi_polygons = [Polygon(vor.vertices[region]) for region in vor.regions if -1 not in region and len(region) > 0]

    # Intersect the Voronoi polygons with the input polygon
    intersection_polygons = [poly.intersection(polygon) for poly in voronoi_polygons]

    # Remove empty polygons
    intersection_polygons = [poly for poly in intersection_polygons if not poly.is_empty]

    # Plot the Voronoi diagram if requested
    if plot or debug:
        fig, ax = plt.subplots()
        ax.axis('off')
        for poly in intersection_polygons:
            if isinstance(poly, Polygon):
                x, y = poly.exterior.xy
                ax.plot(x, y, 'k-')
            elif isinstance(poly, MultiPolygon):
                for sub_poly in poly.geoms:
                    x, y = sub_poly.exterior.xy
                    ax.plot(x, y, 'k-')

        # If keep_outline is True, draw the outline of the polygon
        if keep_outline:
            if isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    x, y = poly.exterior.xy
                    ax.plot(x, y, color='red')
            else:
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='red')

        # If in debug mode, plot the lines, points and Voronoi points as well
        if debug:
            ax.scatter(*zip(*points), color='b', s=5)  # Smaller points
            vor_points_coordinates = [(point[0], point[1]) for point in vor.points]
            ax.scatter(*zip(*vor_points_coordinates), color='g', s=5)  # Smaller points
        
        # Get the current timestamp and format it as a string
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')

        # Serialize the intersection polygons and save them to a file, prefixed with the timestamp
        with open(f'images/out/voronoi.pkl', 'wb') as f:
            pickle.dump((polygon, intersection_polygons), f)

        # Save the figure to a PNG file, prefixed with the timestamp
        plt.savefig(f'images/out/{timestamp}_voronoi.png', format='png')

        #plt.show()  
    
    return intersection_polygons

def color_voronoi(filename, fill_uncolored=True, min_border_width=0.5, max_border_width=2, output_file='images/out/voronoi_colored.png'):
    # Load the polygon and intersection polygons from the file
    with open(filename, 'rb') as f:
        polygon, intersection_polygons = pickle.load(f)

    # Create a new figure and axis
    fig, ax = plt.subplots()
    ax.axis('off')

    # Create a list to store the colored polygons
    colored_polygons = []

    # Create a graph
    G = nx.Graph()

    # Add nodes to the graph
    for i, poly in enumerate(intersection_polygons):
        G.add_node(i)

    # Add edges to the graph
    for i, poly1 in enumerate(intersection_polygons):
        for j, poly2 in enumerate(intersection_polygons):
            if i != j and poly1.touches(poly2):
                G.add_edge(i, j)

    # Color the graph
    color_map = nx.greedy_color(G, strategy=nx.coloring.strategy_connected_sequential_bfs)

    # Define a color palette with 4 shades of gray
    palette = ['#000000', '#555555', '#AAAAAA', '#DDDDDD']

    # Plot the colored Voronoi diagram
    for i, poly in enumerate(intersection_polygons):
        color = palette[color_map[i] % len(palette)]  # Get the color from the palette
        if isinstance(poly, Polygon):
            x, y = poly.exterior.xy
            ax.fill(x, y, color=color)
            colored_polygons.append(Polygon(zip(x, y)))
            if max_border_width > min_border_width:
                border_width = uniform(min_border_width, max_border_width)
                ax.plot(x, y, color='white', linewidth=border_width)
        elif isinstance(poly, MultiPolygon):
            for sub_poly in poly.geoms:
                x, y = sub_poly.exterior.xy
                ax.fill(x, y, color=color)
                colored_polygons.append(Polygon(zip(x, y)))
                if max_border_width > min_border_width:
                    border_width = uniform(min_border_width, max_border_width)
                    ax.plot(x, y, color='white', linewidth=border_width)
    
    if fill_uncolored:
        # Combine all the colored polygons into one
        colored_area = unary_union(colored_polygons)

        # Subtract the colored area from the total area to get the non-colored area
        total_area = unary_union(polygon)
        non_colored_area = total_area.difference(colored_area)

        # If the non-colored area is a Polygon, make it into a list
        if isinstance(non_colored_area, Polygon):
            non_colored_area = [non_colored_area]
        elif isinstance(non_colored_area, MultiPolygon):
            non_colored_area = list(non_colored_area.geoms)

        # Color each non-colored area with a random color from the palette
        for area in non_colored_area:
            color = choice(palette)
            x, y = area.exterior.xy
            ax.fill(x, y, color=color)
            if max_border_width > min_border_width:
                border_width = uniform(min_border_width, max_border_width)
                ax.plot(x, y, color='white', linewidth=border_width)

    # Check if polygon is a MultiPolygon
    if isinstance(polygon, MultiPolygon):
        # Draw the outline of each Polygon in the MultiPolygon in red
        for poly in polygon.geoms:
            x, y = poly.exterior.xy
            ax.plot(x, y, color='red')
    else:
        # Draw the outline of the Polygon in red
        x, y = polygon.exterior.xy
        ax.plot(x, y, color='red')

    # Save the plot to a PNG file
    plt.savefig(output_file)

    # Display the plot
    plt.show()

def create_and_save_masks_from_png(filename, palette = ['#000000', '#555555', '#AAAAAA', '#DDDDDD']):
    # Open the image file
    img = Image.open(filename)
    # Convert the image data to a numpy array
    data = np.array(img)

    # For each color in the palette
    for color in palette:
        # Convert the color to RGB format
        rgb_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

        # Create a mask with the same shape as the image data
        mask = np.all(data[:, :, :3] == rgb_color, axis=-1)  # Only use the first three channels (RGB)

        # Convert the mask to an image
        mask_img = Image.fromarray(mask.astype('uint8') * 255)

        # Save the mask image to a new PNG file
        mask_img.save(f'mask_{color}.png')

polygon = svg_file_to_polygon('images/in/masque.svg', num_points=50, plot=False, mirror=True)
points = generate_points(polygon, num_points=100, mode='grid', debug=False, theta=10)
vor = fill_polygon_with_voronoi(polygon, points=points, plot=True, debug=False)
color_voronoi('images/out/voronoi.pkl',fill_uncolored=True, min_border_width=0.2, max_border_width=3)
create_and_save_masks_from_png('images/out/voronoi_colored.png')