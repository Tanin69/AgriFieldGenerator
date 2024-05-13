from base_class import BaseClass
from shapely.geometry import Point
from random import uniform

class PointsGenerator(BaseClass):
    def __init__(self, svg_height=16257, svg_width=16257, num_points=100, mode='random', debug=False, theta=None):
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.num_points = num_points
        self.mode = mode
        self.debug = debug
        self.theta = theta

    def transform(self, polygon):
        pass

    def display(self, points):
        pass

    def save(self, points, filename):
        pass