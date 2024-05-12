import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mpl_Polygon, PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

def generate_and_plot_polygon(num_sides, curve_probability=0.3, num_curve_points=50):
    # Generate random points
    points = np.random.rand(num_sides, 2)

    # Compute the centroid of the points
    centroid = np.mean(points, axis=0)

    # Compute the angles and distances of the points
    angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
    distances = np.sqrt((points[:, 0] - centroid[0])**2 + (points[:, 1] - centroid[1])**2)

    # Sort the points by angle and distance
    sorted_points = points[np.lexsort((distances, angles))]

    # Close the polygon
    closed_points = np.vstack([sorted_points, sorted_points[0]])

    # Create a Path object
    codes = [Path.MOVETO]
    vertices = [closed_points[0]]

    for i in range(1, len(closed_points)):
        # Randomly decide if this segment should be a line or a curve
        if np.random.rand() < curve_probability:
            # Add a curve
            codes += [Path.CURVE3] * num_curve_points
            # Add a control point for the curve
            control_point = (closed_points[i-1] + closed_points[i]) / 2 + 0.1 * np.random.randn(2)
            # Approximate the curve by a series of short straight lines
            t = np.linspace(0, 1, num_curve_points+1)
            curve_points = ((1-t)**2).reshape(-1,1) * closed_points[i-1] + 2*(1-t).reshape(-1,1)*t.reshape(-1,1)*control_point + t.reshape(-1,1)**2*closed_points[i]
            vertices += list(curve_points[:-1])  # Exclude the last point of the curve
        # Add a line
        codes.append(Path.LINETO)
        vertices.append(closed_points[i])

    # Create the Path object
    path = Path(vertices, codes)

    # Create a patch from the Path
    patch = PathPatch(path, facecolor='orange', lw=2)

    # Plot the patch
    fig, ax = plt.subplots()
    ax.add_patch(patch)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    #plt.show()

    # Create the polygon object
    polygon = Polygon(vertices)

    return polygon  # return the polygon for further use

# Call the function to generate and plot the polygon
polygon = generate_and_plot_polygon(10)

# Get the bounding box of the polygon
minx, miny, maxx, maxy = polygon.bounds

# Generate some random points within the bounding box
random_points = np.random.rand(50, 2)  # adjust this value to change the number of points
random_points[:, 0] = random_points[:, 0] * (maxx - minx) + minx
random_points[:, 1] = random_points[:, 1] * (maxy - miny) + miny

# Create a Voronoi diagram from the random points
vor = Voronoi(random_points)

# Plot the Voronoi diagram
fig, ax = plt.subplots()

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