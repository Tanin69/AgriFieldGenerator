from polygon_utils import svg_file_to_polygon
from voronoi_utils import *

polygon = svg_file_to_polygon('images/in/masque.svg', num_points=20, plot=False, mirror=True)
points = np.random.rand(50, 2)
points = lloyd_relaxation(points, polygon, iterations=2)
vor = fill_polygon_with_voronoi(polygon, points=points, num_lines=4, use_lines=False, plot=True, debug=True)