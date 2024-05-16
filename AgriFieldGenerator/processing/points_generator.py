import os

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon

from .data_processor_base_class import DataProcessorBaseClass

class PointsGenerator(DataProcessorBaseClass):
    def __init__(self,
                 source_path,
                 save_path,
                 save_data_path,
                 svg_height,
                 svg_width,
                 num_points,
                 nx=10,
                 ny=10,
                 rand_offset_x=5,
                 rand_offset_y=5,
                 rand_step_x=2,
                 rand_step_y=5,
                 theta=240):
        
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
        self.theta = theta
        self.points = None

        # Load needed data
        try:
            self.polygon = self.load('polygon.pkl', data_file=True)
        except FileNotFoundError:
            raise FileNotFoundError("Polygon data is missing. Please run the SVGToPolygon class first!")

        # we generate a new set of points, so we need to delete voronoi.pkl and colored.pkl
        if os.path.exists(self.save_data_path + 'voronoi.pkl'):
            os.remove(self.save_data_path + 'voronoi.pkl')
        if os.path.exists(self.save_data_path + 'colored.pkl'):
            os.remove(self.save_data_path + 'colored.pkl')

    def random_generator(self):
        
        minx, miny, maxx, maxy = self.polygon.bounds
        self.points = []
        while len(self.points) < self.num_points:
            pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
            if self.polygon.contains(pnt):
                self.points.append((pnt.x, pnt.y))  # Append as tuple
        
        # Save the data and return the points
        self.save(self.points, 'points.pkl', data_file=True)
        return self.points
    
    def grid_generator(self):
        
        minx, miny, maxx, maxy = self.polygon.bounds

        # Define the number of points in the x and y directions
        nx, ny = (self.nx, self.ny)
        x = np.linspace(minx, maxx, nx)
        y = np.linspace(miny, maxy, ny)
        
        # Generate points with a smaller random offset for each coordinate
        self.points = [(xi + (np.random.rand() - self.rand_offset_x) * (maxx - minx) / (nx * self.rand_step_x), 
                   yi + (np.random.rand() - self.rand_offset_y) * (maxy - miny) / (ny * self.rand_step_y)) 
                  for xi in x for yi in y]
            
        # If theta is not provided, generate a random rotation angle
        if self.theta is None:
            self.theta = np.random.rand() * 2 * np.pi

        # Rotation matrix
        rotation_matrix = np.array([[np.cos(self.theta), -np.sin(self.theta)], 
                                    [np.sin(self.theta), np.cos(self.theta)]])
    
        # Calculate the center of the polygon
        center = [self.polygon.centroid.x, self.polygon.centroid.y]
        
        # Apply rotation to each point around the center of the polygon
        self.points = [np.dot(rotation_matrix, np.subtract(point, center)) + center for point in self.points]
        
        self.save(self.points, 'points.pkl', data_file=True)
        return self.points
    
    def rectangle_generator(self, num_rectangles=10, min_width=1, max_width=5, min_height=1, max_height=5):
        minx, miny, maxx, maxy = self.polygon.bounds
        self.points = []

        for _ in range(num_rectangles):
            # Choose a random location for the bottom left corner of the rectangle
            x0 = np.random.uniform(minx, maxx)
            y0 = np.random.uniform(miny, maxy)

            # Choose a random width and height for the rectangle
            width = np.random.uniform(min_width, max_width)
            height = np.random.uniform(min_height, max_height)

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
