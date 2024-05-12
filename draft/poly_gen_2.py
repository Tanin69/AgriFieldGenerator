import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
from collections import defaultdict
import random

# Number of times to run the script
num_runs = 5

for run in range(num_runs):
    # Generate random points
    points = np.random.rand(50, 2)

    # Compute Voronoi tesselation
    vor = Voronoi(points)

    # Plot Voronoi diagram without original points
    voronoi_plot_2d(vor, show_vertices=False, show_points=False, line_colors='black')

    # List of colors
    colors = ['yellow', 'green', 'brown']

    # Initialize a dictionary to store the color of each region with a default color
    region_colors = {i: colors[0] for i in range(len(vor.point_region))}

    # Build the adjacency list
    adjacency_list = defaultdict(set)
    for ridge in vor.ridge_points:
        adjacency_list[ridge[0]].add(ridge[1])
        adjacency_list[ridge[1]].add(ridge[0])

    # Sort the regions by degree
    regions_sorted_by_degree = sorted(adjacency_list.keys(), key=lambda x: len(adjacency_list[x]), reverse=True)

    # For each region, fill with a color that has not been used by its neighbors
    for region_index in regions_sorted_by_degree:
        region = vor.regions[vor.point_region[region_index]]
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            used_colors = {region_colors.get(i, None) for i in adjacency_list[region_index] if i in region_colors}
            unused_colors = [color for color in colors if color not in used_colors]
            if unused_colors:  # If there are unused colors
                color = random.choice(unused_colors)  # Choose a color at random
                region_colors[region_index] = color
            plt.fill(*zip(*polygon), region_colors[region_index])

    # Set axis limits to match the points' limits
    plt.xlim(points[:, 0].min(), points[:, 0].max())
    plt.ylim(points[:, 1].min(), points[:, 1].max())

    # Save the image
    plt.savefig(f'fields_{run}.png', bbox_inches='tight', pad_inches=0)

    # Clear the plot for the next run
    plt.clf()