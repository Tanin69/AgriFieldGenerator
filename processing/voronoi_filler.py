from base_class import BaseClass
from scipy.spatial import Voronoi

class VoronoiFiller(BaseClass):
    def __init__(self, debug=False, keep_outline=True, svg_height=16257, svg_width=16257):
        self.debug = debug
        self.keep_outline = keep_outline
        self.svg_height = svg_height
        self.svg_width = svg_width

    def transform(self, polygon, points):
        # ... code to fill polygon with Voronoi ...

    def display(self, voronoi):
        # ... code to display Voronoi ...

    def save(self, voronoi, filename):
        # ... code to save Voronoi ...