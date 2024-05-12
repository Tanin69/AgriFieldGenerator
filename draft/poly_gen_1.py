import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

# Generate random points
points = np.random.rand(50, 2)

# Compute Voronoi tesselation
vor = Voronoi(points)

# Plot Voronoi diagram without original points
voronoi_plot_2d(vor, line_colors='black')

# Remove axes
plt.axis('off')

# Save the image
plt.savefig('voronoi.png', bbox_inches='tight', pad_inches=0)

# Show the image
plt.show()