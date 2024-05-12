import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
import triangle as tr
from svg.path import parse_path
from xml.dom import minidom
from svg.path.path import CubicBezier, QuadraticBezier, Line

# Load the SVG file
doc = minidom.parse('image.svg')

# Get the path strings
path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]

# Parse the path strings into Path objects
paths = [parse_path(path_string) for path_string in path_strings]

# Define the number of points to generate per curve
num_points_per_curve = 100  # Increase this number for a denser set of points

# Generate points from the Bézier curves and lines
points = []
for path in paths:
    for curve in path:
        if isinstance(curve, (CubicBezier, QuadraticBezier, Line)):
            t_values = np.linspace(0, 1, num_points_per_curve)
            points.extend([(curve.point(t).real, curve.point(t).imag) for t in t_values])

route_points = np.array(points)

# Generate Voronoi diagram from the route points
vor = Voronoi(route_points)

# Create a new figure and axis
fig, ax = plt.subplots()

# Plot the SVG paths
for path in paths:
    for curve in path:
        if isinstance(curve, (CubicBezier, QuadraticBezier, Line)):
            t_values = np.linspace(0, 1, num_points_per_curve)
            ax.plot([curve.point(t).real for t in t_values], [curve.point(t).imag for t in t_values], color='red', linewidth=2)

# Plot the Voronoi diagram on the same axis
voronoi_plot_2d(vor, ax=ax)

plt.show()  # Display the plot