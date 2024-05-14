from shapely.geometry import Point
import numpy as np

from .data_processing_base_class import DataProcessingBaseClass

class PointsGenerator(DataProcessingBaseClass):
    def __init__(self,
                 source_path,
                 save_path,
                 save_data_path,
                 svg_height,
                 svg_width,
                 num_points,
                 nx=10,
                 ny=25,
                 rand_offset_x=0.5,
                 rand_offset_y=0.5,
                 rand_step_x=1,
                 rand_step_y=1,
                 theta=None):
        
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        
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

    def save_and_return(self, polygon, points):
        data =  points
        self.save(data, 'points.pkl', data_file=True)
        return data

    def random_generator(self):
        polygon = self.load('polygon.pkl', data_file=True)
        minx, miny, maxx, maxy = polygon.bounds
        points = []
        while len(points) < self.num_points:
            pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
            if polygon.contains(pnt):
                points.append((pnt.x, pnt.y))  # Append as tuple
        
        # Save the data and return the points
        return self.save_and_return(polygon, points)
    
    def grid_generator(self):
        
        polygon = self.load('polygon.pkl', data_file=True)

        minx, miny, maxx, maxy = polygon.bounds

        # Define the number of points in the x and y directions
        nx, ny = (self.nx, self.ny)
        x = np.linspace(minx, maxx, nx)
        y = np.linspace(miny, maxy, ny)
        
        # Generate points with a smaller random offset for each coordinate
        points = [(xi + (np.random.rand() - self.rand_offset_x) * (maxx - minx) / (nx * self.rand_step_x), 
                   yi + (np.random.rand() - self.rand_offset_y) * (maxy - miny) / (ny * self.rand_step_y)) 
                  for xi in x for yi in y]
            
        # If theta is not provided, generate a random rotation angle
        if self.theta is None:
            theta = np.random.rand() * 2 * np.pi

        # Rotation matrix
        rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                    [np.sin(theta), np.cos(theta)]])
    
        # Calculate the center of the polygon
        center = [polygon.centroid.x, polygon.centroid.y]
        
        # Apply rotation to each point around the center of the polygon
        points = [np.dot(rotation_matrix, np.subtract(point, center)) + center for point in points]
        
        # Save the data and return the points
        return self.save_and_return(polygon, points)

