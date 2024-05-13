import numpy as np
from xml.dom.minidom import parse

from shapely.geometry import Polygon, MultiPolygon
from svg.path import parse_path, Line, CubicBezier, Move
import matplotlib.pyplot as plt

from .base_class import BaseClass

class SVGToPolygon(BaseClass):
    def __init__(self, svg_height, svg_width, num_points=50, debug=False):
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
        return multi_polygon

    def display(self, polygon):
        fig, ax = plt.subplots()
        ax.set_ylim(0, self.svg_height)  # Set the y-axis limits to match the SVG height
        ax.set_xlim(0, self.svg_width)  # Set the x-axis limits to a fixed value
        if isinstance(polygon, MultiPolygon):
            for polygon in polygon.geoms:
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='red')
        elif isinstance(polygon, Polygon):
            x, y = polygon.exterior.xy
            ax.plot(x, y, color='red')  
        plt.show()

    def save(self, polygon, filename):
        pass