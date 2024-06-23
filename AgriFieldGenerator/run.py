# Copyright (c) [2024] [Didier ALAIN]
# Repository: https://github.com/Tanin69/AgriFieldGenerator
# 
# The project makes it possible to generate patterns of large cultivated fields 
# reproducing as believable as possible the diversity of agricultural 
# landscapes. It allows you to generate texture masks that can be used in the
# world editor of the Enfusion Workbench.
#
# It is released under
# the MIT License. Please see the LICENSE file for details
#
# Enfusion is a game engine developed by Bohemia Interactive for the Arma game series
# The Enfusion Workbench is a creation workbench dedicated to the Enfusion engine.
# 

import argparse
import json
import sys

from processing import *

with open('../config.json') as f:
    config = json.load(f)

# get the configuration values
project_name = config['project_name']
enfusion_texture_masks = config['enfusion_texture_masks']
enfusion_surface_map_resolution = config['enfusion_surface_map_resolution']
palette = config['palette']
enfusion_spline_layer_file = config['source_files']['enfusion_spline_layer_file']
svg_height = config['source_files']['svg_height']
svg_width = config['source_files']['svg_width']
tile_size = config['source_files']['tile_size']
base_dir = config['work_dir']
source_dir = config['paths']['source_dir']
save_dir = config['paths']['save_dir']
save_data_dir = config['paths']['save_data_dir']
svg_file_name = config['source_files']['svg_file_name']
svg_path = base_dir + project_name + "/" + source_dir + svg_file_name
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

# get and parse command line arguments
parser = argparse.ArgumentParser(description='Run the AgriFieldGenerator.')
parser.add_argument('-s', '--svg', action='store_true', default=False, help='Generates a svg file from an Enfusion layer file containing spline entities.')
parser.add_argument('-po', '--polygon', action='store_true', default=False, help='Generates the main polygon from svg file.')
parser.add_argument('-pt', '--points', action='store_true', default=False, help='Generates points schema.')
parser.add_argument('-g', '--generator', choices=['random', 'grid', 'rectangle', 'rect_tiling'], required='-pt' in sys.argv or '--points' in sys.argv, default='random', help='Choose the type of point generator.')
parser.add_argument('-v', '--voronoi', action='store_true', default=False, help='Generates the Voronoi diagram.')
parser.add_argument('--pp_passed', action='store_true', help=argparse.SUPPRESS)
parser.add_argument('-pp', '--pp_curve', type=float, nargs='?', const=True, default=0.5, action='store', metavar='[0-1]', help='Curves some random borders. If passed without a value, defaults to 0.5.')
parser.add_argument('-c', '--colorer', action='store_true', default=False, help='Generates the colored polygons.')
parser.add_argument('-m', '--mask', action='store_true', default=False, help='Generates the masks.')
parser.add_argument('-me', '--merge', action='store_true', help='Merge the masks with Enfusion surface texture masks.')
parser.add_argument('-pl', '--polyline', action='store_true', help='Generate polylines between polygons.')
parser.add_argument('-a', '--all', action='store_true', help='Run all the processors.')
parser.add_argument('-d', '--display', choices=['main_polygon', 'seed_points', 'voronoi'], help='Display the results of a given processor.')

args = parser.parse_args()

# Check the -pp arguments series
if '--pp_curve' in sys.argv or '-pp' in sys.argv:
    args.pp_passed = True
if args.pp_passed and not args.voronoi:
    parser.error("-pp/--pp_curve option requires -v/--voronoi option.")
if args.pp_curve is not True and not 0 <= args.pp_curve <= 1:  # True si -pp est passé sans valeur
    parser.error("-pp/--pp_curve must be an integer or a float between 0 and 1")

# helper functions to call each class
def _create_svg():
    spline_to_svg = SplineToSVG(source_path, save_path, save_data_path, svg_path, svg_height, svg_width, enfusion_surface_map_resolution, enfusion_spline_layer_file)
    splines = spline_to_svg.parse_spline_file()
    spline_to_svg.hermite_to_bezier(splines)

def _create_polygon():
    svg_to_polygon = SVGToPolygon(source_path, save_path, save_data_path, svg_path, svg_height, svg_width, tile_size, num_points)
    svg_to_polygon.process()
    svg_to_polygon.get_polygon_tiles()

def _create_points():
    points_generator = PointsGenerator(
                                    source_path,
                                    save_path,
                                    save_data_path,
                                    svg_path,
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
    elif args.generator == 'rect_tiling':
        points_generator.rectangle_tiling_generator()
    
def _create_voronoi():
    voronoi_filler = VoronoiFiller(source_path, save_path, save_data_path, svg_path, svg_height, svg_width)
    voronoi_filler.process()

def _create_curves_on_voronoi(pp_curve):
    voronoi_filler = VoronoiFiller(source_path, save_path, save_data_path, svg_path, svg_height, svg_width)
    voronoi_filler.pp_curve_voronoi_edges(pp_curve)

def _create_colored_voronoi():
    voronoi_colorer = VoronoiColorer(project_name, source_path, save_path, save_data_path, svg_path, svg_height, svg_width, palette, min_border_width, max_border_width)
    voronoi_colorer.process()

def _create_masks():
    mask_generator = MaskGenerator(source_path, save_path, save_data_path, svg_path, svg_height, svg_width, palette, enfusion_texture_masks)
    mask_generator.process()

def _merge_masks():
    mask_generator = MaskGenerator(source_path, save_path, save_data_path, svg_path, svg_height, svg_width, palette, enfusion_texture_masks)
    mask_generator.merge_masks()

def _create_polylines():
    polyline_generator = PolylineGenerator(enfusion_surface_map_resolution, save_path, save_data_path)
    polyline_generator.generate_polylines()

def _display():
    data_processor = DataProcessorBaseClass(source_path, save_path, save_data_path, svg_path, svg_height, svg_width)
    data_processor.display(args.display)

def run():
    if args.svg:
        _create_svg()
    if args.polygon:
        _create_polygon()
    if args.points:
        _create_points()
    if args.voronoi:
        _create_voronoi()
        if args.pp_curve:
            _create_curves_on_voronoi(args.pp_curve)
    if args.colorer:
        _create_colored_voronoi()
    if args.mask:
        _create_masks()
    if args.merge:
        _merge_masks()
    if args.polyline:
        _create_polylines()
    if args.display:
        _display()

    if args.all:
        _create_svg()
        _create_polygon()
        _create_points()
        _create_voronoi()
        _create_curves_on_voronoi(args.pp_curve)
        _create_colored_voronoi()
        _create_masks()
        _merge_masks()
        _create_polylines()

if __name__ == "__main__":
    run()

