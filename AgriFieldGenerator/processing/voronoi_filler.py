# Copyright (c) [2024] [Didier ALAIN]
# Repository: https://github.com/Tanin69/AgriFieldGenerator
# 
# The project makes it possible to generate patterns of cultivated fields 
# reproducing as faithfully as possible the diversity of agricultural 
# landscapes. It allows you to generate texture masks that can be used in the
# world editor of the Enfusion Workbench.
#
# It is released under the MIT License. Please see the LICENSE file for details.
#
# Enfusion is a game engine developed by Bohemia Interactive.
# The Enfusion Workbench is a creation workbench dedicated to the Enfusion engine.
# 

import os
import glob

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, MultiPolygon
from tqdm import tqdm

from .data_processor_base_class import DataProcessorBaseClass

class VoronoiFiller(DataProcessorBaseClass):
    def __init__(self,
                source_path,
                save_path,
                save_data_path,
                svg_height,
                svg_width):
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.intersection_polygons = None

        # we generate a new set of colored polygons, so we need to delete subsequant files
        glob.glob(self.save_path + '*.png')

        # Load needed data
        try:
            self.polygon = self.load('polygon.pkl', data_file=True)
            self.points = self.load('points.pkl', data_file=True)
        except FileNotFoundError:
            raise FileNotFoundError("Polygon or points data are missing. Please run the SVGToPolygon and PointsGenerator classes first!")
        
    def process(self):     

        # We generate a new voronoi diagram, so we need to delete colored.pkl
        if os.path.exists(self.save_data_path + 'colored.pkl'):
            os.remove(self.save_data_path + 'colored.pkl')

        pbar = tqdm(total=7, desc="Generating Voronoi diagram", unit="step")

        # Convert points to a 2-D array
        points_array = np.array(self.points)
        pbar.update(1)
        # Create the Voronoi diagram
        vor = Voronoi(points_array)
        pbar.update(1)
        # Create polygons for each Voronoi region
        voronoi_polygons = [Polygon(vor.vertices[region]) for region in vor.regions if -1 not in region and len(region) > 0]
        pbar.update(1)
        # Intersect the Voronoi polygons with the input polygon
        self.intersection_polygons = [poly.intersection(self.polygon) for poly in voronoi_polygons]
        pbar.update(1)
        # Clean up the polygons before finding the intersection
        cleaned_polygon = self.polygon.buffer(0)
        cleaned_voronoi_polygons = [Polygon(poly.buffer(0).exterior) for poly in voronoi_polygons]
        pbar.update(1)
        # Remove empty polygons
        intersection_polygons = [poly.intersection(cleaned_polygon) for poly in cleaned_voronoi_polygons]
        pbar.update(1)
        # Save the data and return the voronoi polygons
        self.save(intersection_polygons, 'voronoi.pkl', data_file=True)
        pbar.update(1)
        pbar.close()
        return self.intersection_polygons
    
    def display(self, display_points=False):

        # Fermer les figures existantes
        plt.close('all')

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
        
        # Display points
        if display_points:
            for point in self.points:
                ax.plot(*point, 'ko', markersize=1)
            
        # Display Voronoi fill
        if self.intersection_polygons is None:
            print("Error: self.intersection_polygons is None. You need to generate the Voronoi fill first by calling the process() method.")
            return
        
        for polygon in self.intersection_polygons:
            if isinstance(polygon, Polygon):
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='b')
            elif isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    x, y = poly.exterior.xy
                    ax.plot(x, y, color='b')
        
        plt.show()
        

        
    

    