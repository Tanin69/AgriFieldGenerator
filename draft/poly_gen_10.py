from svgpathtools import svg2paths, wsvg
from shapely.geometry import Point
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np

# Load the SVG file
paths, attributes = svg2paths('image.svg')  # replace with your SVG file path

# Convert the first path in the SVG file to a matplotlib Path
codes = [Path.MOVETO] + [Path.LINETO]*(len(paths[0])-1) + [Path.CLOSEPOLY]
verts = [(segment.start.real, segment.start.imag) for segment in paths[0]] + [(0, 0)]
path = Path(verts, codes)

# Generate random points within the path
minx, miny, maxx, maxy = path.get_extents().bounds
num_points = np.random.randint(5, 51)  # number of polygons between 5 and 50
points = [Point(x, y) for x, y in path.vertices[:-1]]  # add vertices of the path
while len(points) < num_points:
    for _ in range(1000):  # limit the number of attempts to 1000
        point = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if path.contains_point((point.x, point.y)):
            points.append(point)
            break
    else:
        print("Failed to generate a point inside the path after 1000 attempts.")
        break

# Create polygons from the points using Voronoi diagram
vor = Voronoi([point.coords[0] for point in points])
polygons = [Polygon(vor.vertices[region]) for region in vor.regions if len(region) >= 4 and -1 not in region]

fig, ax = plt.subplots()

# Plot the original path
patch = PathPatch(path, fill=False)
ax.add_patch(patch)

# Plot the resulting polygons
for polygon in polygons:
    if polygon.is_empty:
        continue
    color = np.random.rand(3,)  # generate a random color
    if polygon.geom_type == 'Polygon':
        patch = PathPatch(Path(np.array(polygon.exterior.coords)), fill=True, color=color, edgecolor='black')
        ax.add_patch(patch)
    elif polygon.geom_type == 'MultiPolygon':
        for sub_polygon in polygon:
            patch = PathPatch(Path(np.array(sub_polygon.exterior.coords)), fill=True, color=color, edgecolor='black')
            ax.add_patch(patch)

ax.relim()
ax.autoscale_view()

plt.show()