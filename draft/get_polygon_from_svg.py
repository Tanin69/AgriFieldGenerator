import numpy as np
import matplotlib.pyplot as plt
from xml.dom.minidom import parse
from svg.path import parse_path, Line, CubicBezier, Move
from shapely.geometry import Polygon, MultiPolygon
from scipy.spatial import Voronoi, voronoi_plot_2d

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

from shapely.geometry import Point
from shapely.ops import polygonize, unary_union

def fill_polygon_with_voronoi(polygon, num_points=100, plot=False):
    # Get the bounding box of the polygon
    minx, miny, maxx, maxy = polygon.bounds

    # Generate random points within the bounding box
    points = np.random.rand(num_points, 2)
    points[:, 0] = points[:, 0] * (maxx - minx) + minx
    points[:, 1] = points[:, 1] * (maxy - miny) + miny

    # Create the Voronoi diagram
    vor = Voronoi(points)

    # Create polygons for each Voronoi region
    voronoi_polygons = [Polygon(vor.vertices[region]) for region in vor.regions if -1 not in region and len(region) > 0]

    # Intersect the Voronoi polygons with the input polygon
    intersection_polygons = [poly.intersection(polygon) for poly in voronoi_polygons]

    # Remove empty polygons
    intersection_polygons = [poly for poly in intersection_polygons if not poly.is_empty]

    # Plot the Voronoi diagram if requested
    if plot:
        fig, ax = plt.subplots()
        for poly in intersection_polygons:
            x, y = poly.exterior.xy
            ax.plot(x, y, 'k-')
        plt.show()

    return intersection_polygons

polygon = svg_file_to_polygon('images/in/masque.svg', num_points=20, plot=False, mirror=True)
vor = fill_polygon_with_voronoi(polygon, num_points=200, plot=True)