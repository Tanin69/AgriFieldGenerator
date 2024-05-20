import argparse

import json
import sys

from processing import *

with open('../config.json') as f:
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

parser = argparse.ArgumentParser(description='Run the AgriFieldGenerator.')
parser.add_argument('-p', '--points', action='store_true', default=False, help='Generates points schema.')
parser.add_argument('-g', '--generator', choices=['random', 'grid', 'rectangle'], required='-p' in sys.argv or '--points' in sys.argv, default='random', help='Choose the type of point generator.')
parser.add_argument('-v', '--voronoi', action='store_true', default=False, help='Generates the Voronoi diagram.')
parser.add_argument('-c', '--colorer', action='store_true', default=False, help='Generates the colored polygons.')
parser.add_argument('-m', '--mask', action='store_true', default=False, help='Generates the masks.')
parser.add_argument('-me', '--merge', action='store_true', help='Merge the masks with Enfusion surface texture masks.')
parser.add_argument('-a', '--all', action='store_true', help='Run all the processors.')
parser.add_argument('-d', '--display', action='store_true', help='Display the results of executed processors.')

args = parser.parse_args()

svg_to_polygon = SVGToPolygon(source_path, save_path, save_data_path, svg_height, svg_width)
svg_to_polygon.process(svg_path)

if args.points:
    points_generator = PointsGenerator(
                                       source_path,
                                       save_path,
                                       save_data_path,
                                       svg_height,
                                       svg_width,
                                       num_points,
                                       nx,
                                       ny,
                                       rand_offset_x,
                                       rand_offset_y,
                                       rand_step_x,
                                       rand_step_y,
                                       angle,
                                       num_rectangles,
                                       min_width,
                                       max_width,
                                       min_height,
                                       max_height
                                       )
    if args.generator == 'random':
        points_generator.random_generator()
    elif args.generator == 'grid':
        points_generator.grid_generator()
    elif args.generator == 'rectangle':
        points_generator.rectangle_generator()
    
if args.voronoi:
    voronoi_filler = VoronoiFiller(source_path, save_path, save_data_path, svg_height, svg_width)
    voronoi_filler.process()

if args.colorer:
    voronoi_colorer = VoronoiColorer(source_path, save_path, save_data_path, svg_height, svg_width, palette, min_border_width, max_border_width)
    voronoi_colorer.process()

if args.mask:
    mask_generator = MaskGenerator(source_path, save_path, save_data_path, svg_height, svg_width, palette, enfusion_texture_masks)
    mask_generator.process()

if args.merge:
    mask_generator = MaskGenerator(source_path, save_path, save_data_path, svg_height, svg_width, palette, enfusion_texture_masks)
    mask_generator.merge_masks()

if args.all:
    points_generator = PointsGenerator(
                                       source_path,
                                       save_path,
                                       save_data_path,
                                       svg_height,
                                       svg_width,
                                       num_points,
                                       nx,
                                       ny,
                                       rand_offset_x,
                                       rand_offset_y,
                                       rand_step_x,
                                       rand_step_y,
                                       angle,
                                       num_rectangles,
                                       min_width,
                                       max_width,
                                       min_height,
                                       max_height
                                       )
    points_generator.random_generator()
    voronoi_filler = VoronoiFiller(source_path, save_path, save_data_path, svg_height, svg_width)
    voronoi_filler.process()
    voronoi_colorer = VoronoiColorer(source_path, save_path, save_data_path, svg_height, svg_width, palette, min_border_width, max_border_width)
    voronoi_colorer.process()
    mask_generator = MaskGenerator(source_path, save_path, save_data_path, svg_height, svg_width, palette, enfusion_texture_masks)
    mask_generator.process()
    mask_generator.merge_masks()

if args.display:
    if args.points:
        points_generator.display()
    if args.voronoi:
        voronoi_filler.display()
    if args.colorer:
        voronoi_colorer.display()