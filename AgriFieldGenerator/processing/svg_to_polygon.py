import numpy as np
from xml.dom.minidom import parse

from shapely.geometry import Polygon, MultiPolygon
from svg.path import parse_path, Line, CubicBezier, Move
import matplotlib.pyplot as plt

from .data_processing_base_class import DataProcessingBaseClass

class SVGToPolygon(DataProcessingBaseClass):
    def __init__(self, source_path, save_path, save_data_path, svg_height, svg_width, num_points=50, debug=False):
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.num_points = num_points
        self.debug = debug

    def transform(self, svg_file):
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
        multi_polygon = MultiPolygon(polygons)

        # Save the data and return the MultiPolygon
        self.save(multi_polygon, 'polygon.pkl', data_file=True)
        return multi_polygon
