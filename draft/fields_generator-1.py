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

def generate_and_plot_polygon(svg_file, ax):
    # Parse the SVG file
    dom = parse(svg_file)
    # Get the path string
    path_strings = [path.getAttribute('d') for path in dom.getElementsByTagName('path')]
    # Parse the path string into a Path object
    paths = [parse_path(path_string) for path_string in path_strings]
    # Convert the Path object into a Shapely Polygon
    polygons = [Polygon([(point.real, point.imag) for point in path]) for path in paths]
    # Plot each polygon
    for polygon in polygons:
        x, y = polygon.exterior.xy
        ax.plot(x, y)
    # Return the polygons
    return polygons

# Create a single figure and axes
fig, ax = plt.subplots()

# Call the function to generate and plot the polygon
polygon = generate_and_plot_polygon(10, ax)

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