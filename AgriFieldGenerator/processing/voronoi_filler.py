
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
from shapely.geometry import Polygon

from .data_processing_base_class import DataProcessingBaseClass

class VoronoiFiller(DataProcessingBaseClass):
    def __init__(self,
                source_path,
                save_path,
                save_data_path,
                svg_height,
                svg_width,
                ):
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.svg_height = svg_height
        self.svg_width = svg_width

    def transform(self, polygon, points):
        
        #load the polygon and points
        polygon = self.load('polygon.pkl', data_file=True)
        points = self.load('points.pkl', data_file=True)
                
        # Initialize ax
        fig, ax = plt.subplots()
        
        # Convert points to a 2-D array
        points_array = np.array(points)
    
        # Create the Voronoi diagram
        vor = Voronoi(points_array)

        # Create polygons for each Voronoi region
        voronoi_polygons = [Polygon(vor.vertices[region]) for region in vor.regions if -1 not in region and len(region) > 0]

        # Intersect the Voronoi polygons with the input polygon
        intersection_polygons = [poly.intersection(polygon) for poly in voronoi_polygons]

        # Clean up the polygons before finding the intersection
        cleaned_polygon = polygon.buffer(0)
        cleaned_voronoi_polygons = [Polygon(poly.buffer(0).exterior) for poly in voronoi_polygons]

        # Remove empty polygons
        intersection_polygons = [poly.intersection(cleaned_polygon) for poly in cleaned_voronoi_polygons]

        # Save the data and return the MultiPolygon
        data = intersection_polygons
        self.save(data, 'voronoi_fill.pkl', data_file=True)
        return data
    

    