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
 
    # todo : modifier la méthode display pour qu'elle puisse afficher 
    # les données de la méthode transform de la classe voronoi_filler
    # plutôt que de tester le type de données pour afficher les points
    # ou les polygones, il faudrait charger les données de polygon.pkl,
    # points.pkl et voronoi_fill.pkl et les afficher
    
    def display(self, data):
        # Load data from pickle files
        with open(self.save_data_path + 'polygon.pkl', 'rb') as f:
            polygon = pickle.load(f)
        with open(self.save_data_path + 'points.pkl', 'rb') as f:
            points = pickle.load(f)
        with open(self.save_data_path + 'voronoi_fill.pkl', 'rb') as f:
            voronoi_fill = pickle.load(f)

        # Display polygon
        if isinstance(polygon, Polygon):
            x, y = polygon.exterior.xy
            plt.fill(x, y, alpha=0.5, fc='r', ec='none')
        elif isinstance(polygon, MultiPolygon):
            for poly in polygon.geoms:
                x, y = poly.exterior.xy
                plt.fill(x, y, alpha=0.5, fc='r', ec='none')

        # Display points
        for point in points:
            plt.plot(*point, 'ko')

        # Display Voronoi fill
        for polygon in voronoi_fill:
            if isinstance(polygon, Polygon):
                x, y = polygon.exterior.xy
                plt.fill(x, y, alpha=0.4, fc='b', ec='none')
            elif isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    x, y = poly.exterior.xy
                    plt.fill(x, y, alpha=0.4, fc='b', ec='none')

        plt.show()

    """
    def display(self, data):
        fig, ax = plt.subplots()
        ax.set_ylim(0, self.svg_height)  # Set the y-axis limits to match the SVG height
        ax.set_xlim(0, self.svg_width)  # Set the x-axis limits to match the SVG width
    
        if isinstance(data, tuple):  # If data is a tuple of (polygon, points)
            polygon, points = data
            # Display the points
            if points:
                ax.scatter(*zip(*points), color='b', s=5)
            # Display the polygon
            if isinstance(polygon, Polygon):
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='red')
            elif isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    x, y = poly.exterior.xy
                    ax.plot(x, y, color='red')
        elif isinstance(data, MultiPolygon):
            for polygon in data.geoms:
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='red')
        elif isinstance(data, Polygon):
            x, y = data.exterior.xy
            ax.plot(x, y, color='red')
    
        plt.show()
    """
    
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