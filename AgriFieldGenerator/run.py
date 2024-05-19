import json

from processing import *

# with open('../config.json') as f:
with open('D:/Dev/Python/AgriFieldGenerator/config.json') as f:
    config = json.load(f)

# get the configuration values
project_name = config['project_name']
enfusion_texture_masks = config['enfusion_texture_masks']
palette = config['palette']
svg_filename = config['source_files']['svg_filename']
svg_height = config['source_files']['svg_height']
svg_width = config['source_files']['svg_width']
base_dir = config['paths']['base_dir']
source_dir = config['paths']['source_dir']
save_dir = config['paths']['save_dir']
save_data_dir = config['paths']['save_data_dir']
svg_path = base_dir + project_name + "/" + source_dir + svg_filename
source_path = base_dir + project_name + "/" + source_dir
save_path = base_dir + project_name + "/" + save_dir
save_data_path = save_path + save_data_dir
min_border_width = config['borders']['min_border_width']
max_border_width = config['borders']['max_border_width']
num_points = config['point_generators']['random']['num_points']
nx = config['point_generators']['grid']['nx']
ny = config['point_generators']['grid']['ny']
rand_offset_x = config['point_generators']['grid']['rand_offset_x']
rand_offset_y = config['point_generators']['grid']['rand_offset_y']
rand_step_x = config['point_generators']['grid']['rand_step_x']
rand_step_y = config['point_generators']['grid']['rand_step_y']
angle = config['point_generators']['grid']['angle']
num_rectangles = config['point_generators']['rectangle']['num_rectangles']
min_width = config['point_generators']['rectangle']['min_width']
max_width = config['point_generators']['rectangle']['max_width']
min_height = config['point_generators']['rectangle']['min_height']
max_height = config['point_generators']['rectangle']['max_height']

# launch the party
"""
svg_to_polygon = SVGToPolygon(source_path, save_path, save_data_path, svg_height, svg_width)
svg_to_polygon.process(svg_path)
# svg_to_polygon.display()
points_generator = PointsGenerator(source_path, save_path, save_data_path, svg_height, svg_width, num_points, nx, ny, rand_offset_x, rand_offset_y, rand_step_x, rand_step_y, angle, num_rectangles, min_width, max_width, min_height, max_height)
points_generator.random_generator()
# points_generator.display()
voronoi_filler = VoronoiFiller(source_path, save_path, save_data_path, svg_height, svg_width)
voronoi_filler.process()
# voronoi_filler.display()
voronoi_colorer = VoronoiColorer(source_path, save_path, save_data_path, svg_height, svg_width, palette, min_border_width, max_border_width)
voronoi_colorer.process()
# voronoi_colorer.display()
"""
mask_generator = MaskGenerator(source_path, save_path, save_data_path, svg_height, svg_width, palette, enfusion_texture_masks)
# mask_generator.process()
mask_generator.merge_masks()
