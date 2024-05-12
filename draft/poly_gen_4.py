import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
import triangle as tr

# Define the number of points for the main and secondary roads
num_points_main = 500
num_points_secondary = 500

# Define the functions for the main roads
def main_road_func1(x):
    noise = np.random.normal(0, 0.01)  # Add Gaussian noise
    return 0.2 * np.sin(2 * np.pi * x) + 0.1 + noise

def main_road_func2(x):
    noise = np.random.normal(0, 0.01)  # Add Gaussian noise
    return -0.2 * np.sin(2 * np.pi * x) + 0.9 + noise

main_road_funcs = [main_road_func1, main_road_func2]

# Define the functions for the secondary roads
def secondary_road_func1(x):
    noise = np.random.normal(0, 0.01)  # Add Gaussian noise
    return 0.4 * np.sin(2 * np.pi * x) + 0.2 + noise

def secondary_road_func2(x):
    noise = np.random.normal(0, 0.01)  # Add Gaussian noise
    return -0.4 * np.sin(2 * np.pi * x) + 0.8 + noise

def secondary_road_func3(x):
    noise = np.random.normal(0, 0.01)  # Add Gaussian noise
    return np.sin(2 * np.pi * x) + noise

def secondary_road_func4(x):
    noise = np.random.normal(0, 0.01)  # Add Gaussian noise
    return -np.sin(2 * np.pi * x) + 1 + noise

secondary_road_funcs = [secondary_road_func1, secondary_road_func2, secondary_road_func3, secondary_road_func4]

# Generate points for the main roads
main_road_points = np.concatenate([np.array([(xi, func(xi)) for xi in np.linspace(0, 1, num_points_main)]) for func in main_road_funcs])

# Generate points for the secondary roads
secondary_road_points = np.concatenate([np.array([(xi, func(xi)) for xi in np.linspace(0, 1, num_points_secondary)]) for func in secondary_road_funcs])

# Combine the points
points = np.concatenate((main_road_points, secondary_road_points))

# Generate random secondary constraint lines
num_secondary_constraints = 50
secondary_constraints = np.random.rand(num_secondary_constraints, 2, 2)

# Add the secondary constraints to the points and segments
points = np.concatenate((points, secondary_constraints.reshape(-1, 2)))
segments = np.arange(len(points)).reshape(-1, 2)

# Create a Triangle object
A = dict(vertices=points, segments=segments)

# Perform constrained Delaunay triangulation
B = tr.triangulate(A, 'p')

# Generate Voronoi diagram from the Delaunay triangulation
vor = Voronoi(points)

# Create a new figure and axis
fig, ax = plt.subplots()

# Plot the main roads
for func in main_road_funcs:
    x_values = np.linspace(0, 1, num_points_main)
    y_values = func(x_values)
    ax.plot(x_values, y_values, color='red', linewidth=5)  # Plot with red color and thickness 5

# Plot the secondary roads
for func in secondary_road_funcs:
    x_values = np.linspace(0, 1, num_points_secondary)
    y_values = func(x_values)
    ax.plot(x_values, y_values, color='blue', linewidth=2)  # Plot with blue color and thickness 2

# Plot the Voronoi diagram on the same axis
voronoi_plot_2d(vor, ax=ax)

plt.show()  # Display the plot