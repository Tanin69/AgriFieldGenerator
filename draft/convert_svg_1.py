from shapely.geometry import Polygon, Point
from svgpathtools import svg2paths, Line
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import numpy as np

paths, attributes = svg2paths('image.svg')  # replace with your SVG file path

# Convert the paths to lines and plot them
fig, ax = plt.subplots()
for path in paths:
    points = []
    for segment in path:
        if isinstance(segment, Line):
            x = [segment.start.real, segment.end.real]
            y = [segment.start.imag, segment.end.imag]
            ax.plot(x, y, 'k')
            points.extend(list(zip(x, y)))
        else:  # if the segment is not a line, it's a curve
            t = np.linspace(0, 1, num=100)  # parameter for the Bézier curve
            x = np.array([segment.point(t_val).real for t_val in t])
            y = np.array([segment.point(t_val).imag for t_val in t])
            ax.plot(x, y, 'k')
            points.extend(list(zip(x, y)))

    # Convert points to a numpy array
    points = np.array(points)

    # Check if there are at least 4 points
    if len(points) >= 4:
        # Create a Polygon from the points
        polygon = Polygon(points)

        # Get the bounding box of the polygon
        minx, miny, maxx, maxy = polygon.bounds

        # Generate some random points within the bounding box
        random_points = np.random.rand(100, 2)  # adjust this value to change the number of points
        random_points[:, 0] = random_points[:, 0] * (maxx - minx) + minx
        random_points[:, 1] = random_points[:, 1] * (maxy - miny) + miny

        # Create a Voronoi diagram from the random points
        vor = Voronoi(random_points)

        # Plot the Voronoi diagram
        for region in vor.regions:
            if not -1 in region and len(region) > 0:
                poly = [vor.vertices[i] for i in region]
                poly = Polygon(poly)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                if not polygon.is_valid:
                    polygon = polygon.buffer(0)
                if poly.is_valid and polygon.is_valid:
                    poly = poly.intersection(polygon)
                    if poly.is_empty:  # skip if the intersection is empty
                        continue
                    x_poly, y_poly = poly.exterior.xy
                    ax.fill(x_poly, y_poly, 'w')  # fill the polygon with white color
                    ax.plot(x_poly, y_poly, 'b')  # draw the border of the polygon with blue color

plt.show()