import os

import matplotlib.figure
import matplotlib.pyplot as plt
import pickle
from PIL import Image
# from shapely.geometry import Polygon, MultiPolygon

# Increase the maximum image pixels limit
Image.MAX_IMAGE_PIXELS = 400000000

class DataProcessorBaseClass:
    def __init__(self, source_path, save_path, save_data_path):
        self.source_directory = source_path
        self.save_directory = save_path
        self.save_data_directory = save_data_path

    def process(self):
        raise NotImplementedError("Subclasses should implement this!")
    
    def load(self, filename, data_file=False):
        if data_file:
            load_path = self.save_data_directory + filename
            loaded_file = pickle.load(open(load_path, 'rb'))
        else:
            load_path = self.save_data_directory + filename
            loaded_file = Image.open(load_path)
        return loaded_file
    
    def save(self, result, filename, data_file=False, dpi=100):
        if data_file:
            if not os.path.exists(self.save_data_directory):
                os.makedirs(self.save_data_directory)
            with open(self.save_data_directory + filename, 'wb') as f:
                pickle.dump(result, f)
        else:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)
            if isinstance(result, matplotlib.figure.Figure):
                result.savefig(self.save_directory + filename, format='png', dpi=dpi)
            elif isinstance(result, Image.Image):
                result.save(self.save_directory + filename, 'PNG')
            else:
                raise TypeError(f"Unable to save object of type {type(result)}")

    def display(self):
        raise NotImplementedError("Subclasses should implement this!")