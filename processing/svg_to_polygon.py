from base_class import BaseClass
from xml.dom.minidom import parse
from svg.path import parse_path, Line, CubicBezier, Move
from shapely.geometry import Polygon, MultiPolygon

class SVGToPolygon(BaseClass):
    def __init__(self, svg_height=16257, svg_width=16257, num_points=50, debug=False):
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.num_points = num_points
        self.debug = debug

    def transform(self, svg_file):
        pass

    def display(self, polygon):
        pass

    def save(self, polygon, filename):
        pass