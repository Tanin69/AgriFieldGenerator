import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from svg.path import parse_path
from xml.dom.minidom import parse
import xml.dom.minidom

# Load the SVG file
dom = xml.dom.minidom.parse("image.svg")  # replace with your SVG file
path_strings = [path.getAttribute('d') for path in dom.getElementsByTagName('path')]
paths = [parse_path(path_string) for path_string in path_strings]

# Generate points from the SVG curves
points = []
for path in paths:
    for curve in path:
        t_values = np.linspace(0, 1, 100)  # adjust the number of points as needed
        points.extend([(curve.point(t).real, curve.point(t).imag) for t in t_values])

points = np.array(points)

# Compute Voronoi tesselation
vor = Voronoi(points)

# Generate a new Voronoi diagram from the vertices of the previous diagram
new_points = vor.vertices
new_vor = Voronoi(new_points)

# Plot new Voronoi diagram without original points
voronoi_plot_2d(new_vor, line_colors='black')

# Remove axes
plt.axis('off')

# Save the image
plt.savefig('voronoi.png', bbox_inches='tight', pad_inches=0)

# Show the image
plt.show()