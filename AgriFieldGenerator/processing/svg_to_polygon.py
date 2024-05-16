import os

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from svg.path import parse_path, Line, CubicBezier, Move
from xml.dom.minidom import parse

from .data_processor_base_class import DataProcessorBaseClass

class SVGToPolygon(DataProcessorBaseClass):
    def __init__(self, source_path, save_path, save_data_path, svg_height, svg_width, num_points=50):
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.num_points = num_points
        self.multi_polygon = None

        # We generate a new polygon, so we need to delete all the other files
        if os.path.exists(self.save_data_path + 'points.pkl'):
            os.remove(self.save_data_path + 'points.pkl')
        if os.path.exists(self.save_data_path + 'voronoi.pkl'):
            os.remove(self.save_data_path + 'voronoi.pkl')
        if os.path.exists(self.save_data_path + 'colored.pkl'):
            os.remove(self.save_data_path + 'colored.pkl')

    def process(self, svg_file):
        dom = parse(svg_file)
        path_strings = [path.getAttribute('d') for path in dom.getElementsByTagName('path')]
        polygons = []
        for path_string in path_strings:
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
        return self.multi_polygon
    
    def display(self):
        if self.multi_polygon is None:
            print("Error: self.multi_polygon is None. You need to generate the polygon first by calling the process() method.")
            return
    
        # Plot the polygon
        fig, ax = plt.subplots()
        ax.set_ylim(0, self.svg_height)  # Set the y-axis limits to match the SVG height
        ax.set_xlim(0, self.svg_width)  # Set the x-axis limits to a fixed value
        if isinstance(self.multi_polygon, MultiPolygon):
            for poly in self.multi_polygon.geoms:
                ax.plot(*poly.exterior.xy, 'r-')
        else:
            ax.plot(*self.multi_polygon.exterior.xy, 'r-')
        plt.show()
