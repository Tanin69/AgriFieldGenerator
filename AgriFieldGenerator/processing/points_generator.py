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

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
from tqdm import tqdm

from .data_processor_base_class import DataProcessorBaseClass

class PointsGenerator(DataProcessorBaseClass):
    """
    A class used to generate points within a polygon. These points can be 
    generated randomly, in a grid, or within randomly placed rectangles. 
    They be used to generate a Voronoi diagram.

    Attributes
    ----------
    All the attributes from DataProcessorBaseClass and the following. All values
    are read from the configuration file, except points.

    svg_height : int
        The height of the SVG.
    svg_width : int
        The width of the SVG.
    num_points : int
        Only parameter for the random generator : the number of points to
        generate. 
    nx : int
        Grid generator parameter : the number of points in the x direction for
        the grid.
    ny : int
        Grid generator parameter : the number of points in the y direction for
        the grid.
    rand_offset_x : float
        Grid generator parameter : the random offset in the x direction.
    rand_offset_y : float
        Grid generator parameter : the random offset in the y direction.
    rand_step_x : float
        Grid generator parameter : the random step size in the x direction.
    rand_step_y : float
        Grid generator parameter : the random step size in the y direction.
    angle : float
        Grid generator parameter : the rotation angle for the grid.
    num_rectangles : int
        Rectangle generator parameter : the number of rectangles to generate for
        the rectangle generator.
    min_width : float
        Rectangle generator parameter : the minimum width of the rectangles.
    max_width : float
        Rectangle generator parameter : the maximum width of the rectangles.
    min_height : float
        Rectangle generator parameter : the minimum height of the rectangles.
    max_height : float
        Rectangle generator parameter : the maximum height of the rectangles.
    points : list
        The list of generated points.

    Methods
    -------
    random_generator():
        Generates random points within the polygon.
    grid_generator():
        Generates a grid of points within the polygon.
    rectangle_generator():
        Generates points within randomly placed rectangles within the polygon.
    display():
        Displays the polygon and the generated points.
    """
        
    def __init__(self,
                 source_path,
                 save_path,
                 save_data_path,
                 svg_height,
                 svg_width,
                 num_points,
                 nx,
                 ny,
                 rand_offset_x,
                 rand_offset_y,
                 rand_step_x,
                 rand_step_y,
                 angle,
                 num_rectangles,
                 min_width,
                 max_width,
                 min_height,
                 max_height):
        
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.num_points = num_points     
        self.nx = nx
        self.ny = ny
        self.rand_offset_x = rand_offset_x
        self.rand_offset_y = rand_offset_y
        self.rand_step_x = rand_step_x
        self.rand_step_y = rand_step_y
        self.angle = angle
        self.num_rectangles = num_rectangles
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
        self.points = None

        # Load needed data
        try:
            self.polygon = self.load('polygon.pkl', data_file=True)
        except FileNotFoundError:
            raise FileNotFoundError("Polygon data is missing. Please run the SVGToPolygon class first!")

    def random_generator(self):
        """
        Generates random points within the polygon. The number of points is determined by the num_points attribute.
        The points are saved in the 'points.pkl' file.

        Returns
        -------
        list
            A list of generated points.
        """

        self._clean_data()
        
        minx, miny, maxx, maxy = self.polygon.bounds
        # Create a tqdm object with a total
        description = "Generating points"
        description += " " * (26 - len(description))
        pbar = tqdm(total=self.num_points, desc=description, unit="points")
        minx, miny, maxx, maxy = self.polygon.bounds
        self.points = []
        while len(self.points) < self.num_points:
            pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
            if self.polygon.contains(pnt):
                self.points.append((pnt.x, pnt.y))  # Append as tuple
                pbar.update(1)
            
        # Save the data and return the points
        self.save(self.points, 'points.pkl', data_file=True)
        return self.points
    
    def grid_generator(self):
        """
        Generates a grid of points within the polygon. The grid parameters are determined by the nx, ny, rand_offset_x, 
        rand_offset_y, rand_step_x, rand_step_y, and angle attributes. The points are saved in the 'points.pkl' file.

        Returns
        -------
        list
            A list of generated points.
        """
        
        self._clean_data()

        # Create a tqdm object with a total
        description = "Generating points"
        description += " " * (26 - len(description))
        pbar = tqdm(total=5, desc=description, unit="step")
        minx, miny, maxx, maxy = self.polygon.bounds

        # Define the number of points in the x and y directions
        nx, ny = (self.nx, self.ny)
        x = np.linspace(minx, maxx, nx)
        y = np.linspace(miny, maxy, ny)
        pbar.update(1)
        
        # Generate points with a smaller random offset for each coordinate
        self.points = [(xi + (np.random.rand() - self.rand_offset_x) * (maxx - minx) / (nx * self.rand_step_x), 
                   yi + (np.random.rand() - self.rand_offset_y) * (maxy - miny) / (ny * self.rand_step_y)) 
                  for xi in x for yi in y]
        pbar.update(1)
            
        # If angle is not provided, generate a random rotation angle
        if self.angle is None:
            self.angle = np.random.rand() * 2 * np.pi

        # Rotation matrix
        rotation_matrix = np.array([[np.cos(self.angle), -np.sin(self.angle)], 
                                    [np.sin(self.angle), np.cos(self.angle)]])
        pbar.update(1)
    
        # Calculate the center of the polygon
        center = [self.polygon.centroid.x, self.polygon.centroid.y]
        
        # Apply rotation to each point around the center of the polygon
        self.points = [np.dot(rotation_matrix, np.subtract(point, center)) + center for point in self.points]
        pbar.update(1)
        
        self.save(self.points, 'points.pkl', data_file=True)
        pbar.update(1)
        pbar.close()
        return self.points
    
    def rectangle_generator(self):
        """
        Generates points within randomly placed rectangles within the polygon. The rectangle parameters are determined by 
        the num_rectangles, min_width, max_width, min_height, and max_height attributes. The points are saved in the 'points.pkl' file.

        Returns
        -------
        list
            A list of generated points.
        """
        self._clean_data()
        minx, miny, maxx, maxy = self.polygon.bounds
        self.points = []
  
        description = "Generating points"
        description += " " * (26 - len(description))
        
        for _ in tqdm(range(self.num_rectangles), desc=description, unit="rectangle"):
            # Choose a random location for the bottom left corner of the rectangle
            x0 = np.random.uniform(minx, maxx)
            y0 = np.random.uniform(miny, maxy)

            # Choose a random width and height for the rectangle
            width = np.random.uniform(self.min_width, self.max_width)
            height = np.random.uniform(self.min_height, self.max_height)

            # Make sure the rectangle fits within the polygon bounds
            x1 = min(x0 + width, maxx)
            y1 = min(y0 + height, maxy)

            # Generate points within the rectangle
            x = np.linspace(x0, x1, self.nx)
            y = np.linspace(y0, y1, self.ny)
            self.points.extend((xi, yi) for xi in x for yi in y)

        # Save the data and return the points
        self.save(self.points, 'points.pkl', data_file=True)
        return self.points

    def display(self):
        """
        Displays the polygon and the generated points. If the points have not been generated yet, an error message is printed.
        """
        
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
        if self.points is None:
            print("Error: self.points is None. You need to generate points first by calling one of the *_generator() method.")
            return
            
        for point in self.points:
            ax.plot(*point, 'ko', markersize=1)
        
        plt.show()

    def _clean_data(self):
        """
        Deletes 'voronoi.pkl' and 'colored.pkl' files if they exist. This method is called before generating a new set of points.
        """
        # we generate a new set of points, so we need to delete voronoi.pkl and colored.pkl
        if os.path.exists(self.save_data_path + 'voronoi.pkl'):
            os.remove(self.save_data_path + 'voronoi.pkl')
        if os.path.exists(self.save_data_path + 'colored.pkl'):
            os.remove(self.save_data_path + 'colored.pkl')

