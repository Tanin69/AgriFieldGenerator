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

import os

import matplotlib.figure
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pickle
from PIL import Image
from shapely.geometry import MultiPolygon, Polygon

# Increase the maximum image pixels limit beacause Enfusion image files are very large
Image.MAX_IMAGE_PIXELS = 400000000

class DataProcessorBaseClass:
    """
    Base class for data processing tasks. Provides methods for loading and saving data, 
    and a method for processing data that should be implemented by subclasses.
    """
    def __init__(self, source_path, save_path, save_data_path, svg_path, svg_height, svg_width):
        """
        Initializes a new instance of the class. Sets the source, save, and save data directories.

        :param source_path: The path to the source directory where the input data is located.
        :param save_path: The path to the directory where the processed data should be saved.
        :param save_data_path: The path to the directory where any additional data should be saved.
        """
        self.source_directory = source_path
        self.save_directory = save_path
        self.save_data_directory = save_data_path
        self.svg_path = svg_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.points = None
        self.polygon = None
        self.polygons = None

    def process(self):
        """
        This method should be implemented by subclasses. It should contain the logic for processing the data.
        """
        raise NotImplementedError("Subclasses should implement this!")
    
    def load(self, filename, data_file=False):
        """
        Loads a file from the save data directory. If `data_file` is `True`, the file is loaded using `pickle`. 
        Otherwise, the file is loaded as an image.

        :param filename: The name of the file to load.
        :param data_file: A boolean indicating whether the file is a data file (default is False).
        :return: The loaded file.
        """
        if data_file:
            load_path = self.save_data_directory + filename
            loaded_file = pickle.load(open(load_path, 'rb'))
        else:
            load_path = self.save_data_directory + filename
            loaded_file = Image.open(load_path)
        return loaded_file
    
    def save(self, result, filename, data_file=False, dpi=100):
        """
        Saves a file to the save directory or the save data directory, depending on the value of `data_file`. 
        If `data_file` is `True`, the file is saved using `pickle`. Otherwise, the file is saved as an image. 
        If the result is a `matplotlib.figure.Figure`, it is saved with the specified DPI.

        :param result: The result to save.
        :param filename: The name of the file to save.
        :param data_file: A boolean indicating whether the file is a data file (default is False).
        :param dpi: The DPI to use when saving a `matplotlib.figure.Figure` (default is 100).
        """
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

    def display(self, file_to_display):
        """
       

        """
        try:
            self.polygon = self.load('polygon.pkl', data_file=True)
        except FileNotFoundError:
            raise FileNotFoundError("Polygon data are missing. Please run the relevant generator(s) first.")

        if file_to_display == 'main_polygon':
            self._plot()
            return

        if file_to_display == 'seed_points':
            try:
                self.points = self.load('points.pkl', data_file=True)
            except FileNotFoundError:
                raise FileNotFoundError("Main polygon or seed points data are missing. Please run the relevant generator(s) first.")
            self._plot(points=True, bounding_box=True)
            return

        if file_to_display == 'voronoi':
            try:
                self.polygons = self.load('voronoi.pkl', data_file=True)
            except FileNotFoundError:
                raise FileNotFoundError("Voronoi diagram data are missing. Please run the relevant generator(s) first.")
            self._plot(polygons=True)
            return

    def _plot(self, points=False, bounding_box=False, polygons=False):
        
        # Create a new figure and axes
        fig, ax = plt.subplots()
        
        # Set the limits of the axes to the SVG dimensions
        ax.set_xlim(0, self.svg_width)
        ax.set_ylim(0, self.svg_height)
        
        # Display polygon
        if isinstance(self.polygon, Polygon):
            x, y = self.polygon.exterior.xy
            ax.fill(x, y, alpha=0.5, fc='r', ec='none')
        elif isinstance(self.polygon, MultiPolygon):
            for poly in self.polygon.geoms:
                x, y = poly.exterior.xy
                ax.plot(x, y, color='r')

        if bounding_box:
            # Display bounding box
            minx, miny, maxx, maxy = self.polygon.bounds
            rect = patches.Rectangle((minx, miny), maxx-minx, maxy-miny, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
        
        if points:    
            # Display points
            for point in self.points:
                ax.plot(*point, 'ko', markersize=1)

        if polygons:
            for polygon in self.polygons:
                if isinstance(polygon, Polygon):
                    x, y = polygon.exterior.xy
                    ax.plot(x, y, color='b')
                elif isinstance(polygon, MultiPolygon):
                    for poly in polygon.geoms:
                        x, y = poly.exterior.xy
                        ax.plot(x, y, color='b')
        
        plt.show()


