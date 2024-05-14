import json

from processing import *

# with open('../config.json') as f:
with open('D:/Dev/Python/AgriFieldGenerator/config.json') as f:
    config = json.load(f)

# get the configuration values
base_dir = config['base_dir']
project_name = config['project_name']
svg_filename = config['svg_filename']
svg_height = config['svg_height']
svg_width = config['svg_width']
source_dir = config['source_dir']
save_dir = config['save_dir']
save_data_dir = config['save_data_dir']
svg_path = base_dir + project_name + "/" + source_dir + svg_filename
source_path = base_dir + project_name + "/" + source_dir
save_path = base_dir + project_name + "/" + save_dir
save_data_path = save_path + save_data_dir


# launch the party
svg_to_polygon = SVGToPolygon(source_path, save_path, save_data_path, svg_height, svg_width)
polygon = svg_to_polygon.transform(svg_path)
# svg_to_polygon.display(polygon)
points_generator = PointsGenerator(source_path, save_path, save_data_path, svg_height, svg_width, 50)
points = points_generator.grid_generator()
# points_generator.display(points)
voronoi_filler = VoronoiFiller(source_path, save_path, save_data_path, svg_height, svg_width)
data = voronoi_filler.transform('polygon.pkl', 'points.pkl')
voronoi_filler.display(data)