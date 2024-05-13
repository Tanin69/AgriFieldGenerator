import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mpl_Polygon, PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

from svg.path import parse_path
from xml.dom.minidom import parse

from svg.path import Line, Move

from svg.path import CubicBezier

from shapely.geometry import MultiPolygon

def generate_and_plot_polygon(svg_file, ax):
    dom = parse(svg_file)
    path_strings = [path.getAttribute('d') for path in dom.getElementsByTagName('path')]
    paths = [parse_path(path_string) for path_string in path_strings]

    polygons = []
    points = []
    for path in paths:
        for command in path:
            if isinstance(command, Line) or isinstance(command, CubicBezier):
                if isinstance(command, Line):
                    points.append((command.end.real, command.end.imag))
                else:  # CubicBezier
                    for t in np.linspace(0, 1, num=20):
                        point = command.point(t)
                        points.append((point.real, point.imag))
            elif isinstance(command, Move):
                if points and len(points) >= 4:  # Ensure there are at least 4 points
                    polygons.append(Polygon(points))
                    points = []  # Start a new polygon
                points.append((command.start.real, command.start.imag))

    if points and len(points) >= 4:  # Add the last polygon if it has at least 4 points
        polygons.append(Polygon(points))

    # Create a MultiPolygon from all the polygons
    multi_polygon = MultiPolygon(polygons)

    # Plot the polygons
    for polygon in multi_polygon:
        x, y = polygon.exterior.xy
        ax.plot(x, y)

    return multi_polygon

# Create a single figure and axes
fig, ax = plt.subplots()

# Call the function to generate and plot the polygon
polygon = generate_and_plot_polygon('image.svg', ax)

# Get the bounding box of the polygon
minx, miny, maxx, maxy = polygon.bounds

# Generate some random points within the bounding box
random_points = np.random.rand(200, 2)  # adjust this value to change the number of points
random_points[:, 0] = random_points[:, 0] * (maxx - minx) + minx
random_points[:, 1] = random_points[:, 1] * (maxy - miny) + miny

# Create a Voronoi diagram from the random points
vor = Voronoi(random_points)

# Iterate over the Voronoi ridges
for ridge in vor.ridge_vertices:
    if -1 not in ridge:
        # Create a LineString from the ridge
        line = LineString([vor.vertices[i] for i in ridge])
        # Check if the polygon is valid
        if polygon.is_valid:
            # Intersect the line with the polygon
            intersection = polygon.intersection(line)
            if intersection.is_empty:
                continue
            if intersection.geom_type == 'LineString':
                intersection = [intersection]
            elif intersection.geom_type == 'MultiLineString':
                intersection = list(intersection.geoms)
            for segment in intersection:
                x, y = segment.xy
                ax.plot(x, y, 'k')
        else:
            # If the polygon is still invalid, try to fix it by performing a unary union operation
            polygon = unary_union(polygon)

# Plot the points
# ax.plot(random_points[:, 0], random_points[:, 1], 'o')

# Plot the polygon
x, y = polygon.exterior.xy
ax.plot(x, y, 'r')

plt.show()