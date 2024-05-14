import os

import matplotlib.figure
import matplotlib.pyplot as plt
import pickle
from PIL import Image
from shapely.geometry import Polygon, MultiPolygon

class DataProcessingBaseClass:
    def __init__(self, source_path, save_path, save_data_path):
        self.source_directory = source_path
        self.save_directory = save_path
        self.save_data_directory = save_data_path

    def transform(self, input_data):
        raise NotImplementedError("Subclasses should implement this!")
   
    def display(self, data):
        # Load data from pickle files
        with open(self.save_data_path + 'polygon.pkl', 'rb') as f:
            polygon = pickle.load(f)
        with open(self.save_data_path + 'points.pkl', 'rb') as f:
            points = pickle.load(f)
        with open(self.save_data_path + 'voronoi_fill.pkl', 'rb') as f:
            voronoi_fill = pickle.load(f)
        
        # Close all existing figures
        plt.close('all')

        # Create a new figure and axes
        fig, ax = plt.subplots()
        
        # Set the limits of the axes to the SVG dimensions
        ax.set_xlim(0, self.svg_width)
        ax.set_ylim(0, self.svg_height)
        
        # Display polygon
        if isinstance(polygon, Polygon):
            x, y = polygon.exterior.xy
            ax.fill(x, y, alpha=0.5, fc='r', ec='none')
        elif isinstance(polygon, MultiPolygon):
            for poly in polygon.geoms:
                x, y = poly.exterior.xy
                ax.plot(x, y, color='r')
        
        # Display points
        for point in points:
            ax.plot(*point, 'ko')
        
        # Display Voronoi fill
        for polygon in voronoi_fill:
            if isinstance(polygon, Polygon):
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='b')
            elif isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    x, y = poly.exterior.xy
                    ax.plot(x, y, color='b')
        
        plt.show()
  
    def save(self, result, filename, data_file=False):
        if data_file:
            if not os.path.exists(self.save_data_directory):
                os.makedirs(self.save_data_directory)
            with open(self.save_data_directory + filename, 'wb') as f:
                pickle.dump(result, f)
        else:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)
            if isinstance(result, matplotlib.figure.Figure):
                result.savefig(self.save_directory + filename, format='png')
            elif isinstance(result, Image.Image):
                result.save(self.save_directory + filename, 'PNG')
            else:
                raise TypeError(f"Unable to save object of type {type(result)}")

    def load(self, filename, data_file=False):
        if data_file:
            load_path = self.save_data_directory + filename
            loaded_file = pickle.load(open(load_path, 'rb'))
        else:
            load_path = self.save_data_directory + filename
            loaded_file = Image.open(load_path)
        return loaded_file