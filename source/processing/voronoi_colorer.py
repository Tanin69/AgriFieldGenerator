from .base_class import BaseClass
from PIL import Image

class VoronoiColorer(BaseClass):
    def __init__(self, fill_uncolored=True, min_border_width=0.1, max_border_width=20, output_file='images/out/voronoi_colored.png'):
        self.fill_uncolored = fill_uncolored
        self.min_border_width = min_border_width
        self.max_border_width = max_border_width
        self.output_file = output_file

    def transform(self, filename):
        pass

    def display(self, image):
        pass

    def save(self, image, filename):
        pass