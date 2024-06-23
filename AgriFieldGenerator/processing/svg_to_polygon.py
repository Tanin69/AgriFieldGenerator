# Copyright (c) [2024] [Didier ALAIN]
# Repository: https://github.com/Tanin69/AgriFieldGenerator
# 
# The project makes it possible to generate patterns of large cultivated fields 
# reproducing as believable as possible the diversity of agricultural 
# landscapes. It allows you to generate texture masks that can be used in the
# world editor of the Enfusion Workbench.
#
# It is released under the MIT License. Please see the LICENSE file for details.
#
# Enfusion is a game engine developed by Bohemia Interactive for the Arma game series
# The Enfusion Workbench is a creation workbench dedicated to the Enfusion engine.
# 

from xml.dom.minidom import parse

import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
from svg.path import parse_path, Line, CubicBezier, Move
from tqdm import tqdm

from .data_processor_base_class import DataProcessorBaseClass

class SVGToPolygon(DataProcessorBaseClass):
    """
    A class used to convert SVG files to polygons.

    Attributes
    ----------
    source_path : str
        The path to the source SVG file.
    save_path : str
        The path where the output files will be saved.
    save_data_path : str
        The path where the data files will be saved.
    svg_height : int
        The height of the SVG file.
    svg_width : int
        The width of the SVG file.
    tile_size : int
        The size of the tiles.
    num_points : int
        The number of points to generate for each line or curve in the SVG file.
    multi_polygon : MultiPolygon
        The generated MultiPolygon object.

    Methods
    -------
    process(svg_file)
        Processes the SVG file and generates a MultiPolygon object.
    display()
        Displays the generated MultiPolygon object.
    get_polygon_tiles()
        Gets the tile indices for each polygon in the MultiPolygon object.
    _get_tile_index(x, y)
        Gets the tile index for a given point.
    """

    def __init__(self, source_path, save_path, save_data_path, svg_path, svg_height, svg_width, tile_size, num_points):
        """
        Constructs all the necessary attributes for the SVGToPolygon object.

        Parameters
        ----------
        source_path : str
            The path to the source SVG file.
        save_path : str
            The path where the output files will be saved.
        save_data_path : str
            The path where the data files will be saved.
        svg_height : int
            The height of the SVG file.
        svg_width : int
            The width of the SVG file.
        tile_size : int
            The size of the tiles.
        num_points : int
            The number of points to generate for each line or curve in the SVG file.
        """
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path, svg_path=svg_path, svg_height=svg_height, svg_width=svg_width)
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.svg_path = svg_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.tile_size=tile_size
        self.tile_step = int(self.tile_size/20)
        self.num_x_tiles = round(self.svg_width / self.tile_size)
        self.num_points = num_points
        self.multi_polygon = None

    def process(self):
        """
        Processes the SVG file and generates a MultiPolygon object.

        Parameters
        ----------
        svg_file : str
            The path to the SVG file.

        Returns
        -------
        MultiPolygon
            The generated MultiPolygon object.
        """
        # We generate a new polygon, so we need to delete all the other files
        """
        if os.path.exists(self.save_data_path + 'points.pkl'):
            os.remove(self.save_data_path + 'points.pkl')
        if os.path.exists(self.save_data_path + 'voronoi.pkl'):
            os.remove(self.save_data_path + 'voronoi.pkl')
        if os.path.exists(self.save_data_path + 'colored.pkl'):
            os.remove(self.save_data_path + 'colored.pkl')
        """
        dom = parse(self.svg_path)
        path_strings = [path.getAttribute('d') for path in dom.getElementsByTagName('path')]
        polygons = []
        description = "Generating main polygon"
        description += " " * (26 - len(description))
        for path_string in tqdm(path_strings, desc=description, unit=" path"):
            path = parse_path(path_string)
            points = []
            for command in path:
                if isinstance(command, Line) or isinstance(command, CubicBezier):
                    if isinstance(command, Line):
                        points.append((command.end.real, self.svg_height - command.end.imag))
                    else:  # CubicBezier
                        for t in np.linspace(0, 1, num=self.num_points):
                            point = command.point(t)
                            points.append((point.real, self.svg_height - point.imag))
                elif isinstance(command, Move):
                    if points and len(points) >= 4:  # Ensure there are at least 4 points
                        polygons.append(Polygon(points))
                        points = []  # Start a new polygon
                    points.append((command.start.real, self.svg_height - command.start.imag))

            if points and len(points) >= 4:  # Add the last polygon if it has at least 4 points
                polygons.append(Polygon(points))

        # Create a MultiPolygon from all the polygons
        self.multi_polygon = MultiPolygon(polygons)

        # Save the data and return the MultiPolygon
        self.save(self.multi_polygon, 'polygon.pkl', data_file=True)
        # print(f"The main polygon data has been saved to {self.save_data_path}polygon.pkl.")
        return self.multi_polygon
    
    def get_polygon_tiles(self):
        """
        Gets the tile indices for each polygon in the MultiPolygon object.

        Returns
        -------
        list
            The list of tile indices.
        """

        # TODO : get polygons from polygon.pkl and move this method (and private associated methods) to EnfusionUtils
        
        # Get the tile indices for each polygon
        if self.multi_polygon is None:
            print("Error: self.multi_polygon is None. You need to generate the polygon first by calling the process() method.")
            return
        tile_indices = set()

        # Iterate over the tiles in the bounding box of the MultiPolygon
        minx, miny, maxx, maxy = self.multi_polygon.bounds
        for x in range(int(minx), int(maxx) + 1, self.tile_step):
            for y in range(int(miny), int(maxy) + 1, self.tile_step):
                point = Point(x, y)
                if self.multi_polygon.contains(point):
                    tile_index = self._get_tile_index(x, y)
                    tile_indices.add(tile_index)
        tile_indices = sorted(list(tile_indices))
                
        # Save the tile indices to a file
        with open(self.save_path + "polygon_tiles.txt", 'w') as file:
            # Write each tile index to the file
            for tile_index in tile_indices:
                file.write(f"{tile_index}\n")
        
        print(f"{len(tile_indices)} tiles could be changed after importing masks in Enfusion.\nFor the list of tile indices, see {self.save_path + "polygon_tiles.txt"}")
        return tile_indices
   
    def _get_tile_index(self, x, y):
        """
        Gets the tile index for a given point.

        Parameters
        ----------
        x : int
            The x-coordinate of the point.
        y : int
            The y-coordinate of the point.

        Returns
        -------
        int
            The tile index.
        """
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        tile_index = int(tile_y * self.num_x_tiles + tile_x)
        return tile_index


