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
import glob
import random

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import LineString, Point, Polygon, MultiPolygon
from shapely.ops import linemerge
from tqdm import tqdm

from .data_processor_base_class import DataProcessorBaseClass

class VoronoiFiller(DataProcessorBaseClass):
    """
    A class used to fill a polygon with a Voronoi diagram. The Voronoi diagram is generated from a set of points within the polygon.

    Attributes
    ----------
    All the attributes from DataProcessorBaseClass and the following. All values
    are read from the configuration file, except intersection_polygons.

    svg_height : int
        The height of the SVG.
    svg_width : int
        The width of the SVG.
    intersection_polygons : list
        The list of polygons resulting from the intersection of the Voronoi diagram and the input polygon.

    Methods
    -------
    process():
        Generates the Voronoi diagram and intersects it with the input polygon.
    display(display_points=False):
        Displays the input polygon, the generated points, and the Voronoi diagram.
    """
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
        self.curved_edges = {}
        self.curved_polygons = []
        self.cleaned_polygons = []

        # we generate a new set of colored polygons, so we need to delete subsequant files
        glob.glob(self.save_path + '*.png')

        # Load needed data
        try:
            self.polygon = self.load('polygon.pkl', data_file=True)
            self.points = self.load('points.pkl', data_file=True)
        except FileNotFoundError:
            raise FileNotFoundError("Polygon or points data are missing. Please run the SVGToPolygon and PointsGenerator classes first!")
        
    def process(self):
        """
        Generates the Voronoi diagram from the points within the polygon and intersects it with the input polygon. 
        The resulting polygons are saved in the 'voronoi.pkl' file.

        Returns
        -------
        list
            A list of polygons resulting from the intersection of the Voronoi diagram and the input polygon.
        """     

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
        self.intersection_polygons = [poly.intersection(cleaned_polygon) for poly in cleaned_voronoi_polygons]
        pbar.update(1)
        
        # Save the data and return the voronoi polygons
        self.save(self.intersection_polygons, 'voronoi.pkl', data_file=True)
        pbar.update(1)
        pbar.close()
        print(f"Number of generated polygons: {len(self.intersection_polygons)}")

        return self.intersection_polygons      
    
    def pp_filter_triangles(self):
        """
        Post-processes the result of the process method by removing polygons that are triangles.

        Returns
        -------
        list
            A list of polygons resulting from the intersection of the Voronoi diagram and the input polygon, with triangles removed.
        """
        if self.intersection_polygons is None:
            print("Error: self.intersection_polygons is None. You need to generate the Voronoi fill first by calling the process() method.")
            return

        non_triangle_polygons = []
        for polygon in self.intersection_polygons:
            if isinstance(polygon, Polygon):
                if len(polygon.exterior.coords) > 4:  # A triangle has 3 points, but the first point is repeated at the end, so we have 4 coordinates
                    non_triangle_polygons.append(polygon)
            elif isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    if len(poly.exterior.coords) > 4:
                        non_triangle_polygons.append(poly)

        self.intersection_polygons = non_triangle_polygons
        # Save the data and return the voronoi polygons
        self.save(self.intersection_polygons, 'voronoi.pkl', data_file=True)
        return self.intersection_polygons

    def pp_curve_voronoi_edges(self, curve_probability=0.4):
        try:
            voronoi_polygons = self.load('voronoi.pkl', data_file=True)
        except FileNotFoundError:
            raise FileNotFoundError("Voronoi data is missing. Please run the process method of VoronoiFiller class first!")
        
        curved_polygons = []
        print(f"Number of polygons before curving borders: {len(voronoi_polygons)}")
        
        for polygon in voronoi_polygons:
            if isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    curved_polygons.append(self._curve_polygon_edges_random(poly, curve_probability))
            else:
                curved_polygons.append(self._curve_polygon_edges_random(polygon, curve_probability))
        print(f"Number of polygons after curving borders: {len(curved_polygons)}")
        self.curved_polygons = curved_polygons
        curved_polygons = self._clean_edges()
        # tranform the list of LineString to polygons
        polygon_objects = [Polygon(linemerge([line_string for line_string in sublist]).coords) for sublist in curved_polygons]
        # Save the data and return the voronoi polygons
        self.curved_polygons = polygon_objects
        self.save(self.curved_polygons, 'voronoi.pkl', data_file=True)
        return self.curved_polygons

    def display(self, display_points=False):
        """
        Displays the input polygon, the generated points, and the Voronoi diagram. If the Voronoi diagram has not been generated yet, 
        an error message is printed.

        Parameters
        ----------
        display_points : bool, optional
            If True, the points used to generate the Voronoi diagram are displayed. Default is False.
        """

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
        
        for polygon in self.curved_polygons:
            if isinstance(polygon, Polygon):
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='b')
            elif isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    x, y = poly.exterior.xy
                    ax.plot(x, y, color='b')
        
        plt.show()  

    def _curve_polygon_edges_random(self, polygon, curve_probability):
        curved_polygon_edges = []
        num_vertices = len(polygon.exterior.coords) - 1
        index_point = 1
        # Iterate over the edges of the polygon
        for i in range(num_vertices):
            if self.polygon.intersects(Point(polygon.exterior.coords[i])):
                start_point, end_point = polygon.exterior.coords[i], polygon.exterior.coords[i+1]
                old_edge = LineString([start_point, end_point])
                if random.uniform(0, 1) < curve_probability:  # the edge is a line, curve it with a certain probability
                    control_points = self._generate_control_points(start_point, end_point, 10)
                    new_edge = self._generate_pseudo_curve(start_point, control_points, end_point)
                else:  # the edge is a line and we don't curve it
                    new_edge = old_edge
            # Add the new edge to the resulting polygon
            else:
                if i < num_vertices:
                    new_edge = LineString(polygon.exterior.coords[i:i+2])
                else:
                    new_edge = LineString([polygon.exterior.coords[i], polygon.exterior.coords[0]])   
            curved_polygon_edges.append(new_edge)
            index_point += 1
        return curved_polygon_edges
        # return Polygon(curved_polygon_points)  
       
    def _generate_control_points(self, start_point, end_point, num_points, min_spacing=0.1, max_offset=0.1):
        points = []
        segment_length = np.linalg.norm(np.array(end_point) - np.array(start_point))
        min_spacing = min_spacing * segment_length
        max_offset = max_offset * segment_length
        positions = np.linspace(0.25, 0.75, num_points + 2)[1:-1]  # exclude the ends
        for t in positions:
            offset = np.random.uniform(-max_offset, max_offset)
            point = (1 - t) * np.array(start_point) + t * np.array(end_point) + offset
            if points and np.linalg.norm(point - points[-1]) < min_spacing:
                continue  # skip this point if it's too close to the previous one
            points.append(point)
        return points
    
    def _generate_pseudo_curve(self, start_point, control_points, end_point):
        # Combine all points
        points = [start_point] + control_points + [end_point]
        
        def de_casteljau(t, points):
            if len(points) == 1:
                return points[0]           
            new_points = []
            for i in range(len(points) - 1):
                x = (1 - t) * points[i][0] + t * points[i + 1][0]
                y = (1 - t) * points[i][1] + t * points[i + 1][1]
                new_points.append((x, y))
            return de_casteljau(t, new_points)
        
        # Generate curve points
        curve_points = [de_casteljau(t, points) for t in np.linspace(0.0, 1.0, 100)]
        return LineString(curve_points)
    
    def _find_adjacent_polygon(self, poly_collection, original_polygon, original_edge_vertices):
        """
        Find the polygon in the collection that shares the edge with the original polygon.

        param poly_collection: a collection of polygons
        param original_polygon: the original polygon
        param original_edge_vertices: the edge vertices of the original polygon
        return: the adjacent polygon if found, None otherwise

        TODO: accept more types of polygon collections. Now it only accepts a list of polygons.
        """
        for polygon in poly_collection:
            if polygon == original_polygon:
                continue
            else:
                for edge in list(polygon):
                    edge_vertices = LineString([edge.coords[0], edge.coords[len(edge.coords) - 1]])
                    if edge_vertices == original_edge_vertices or edge_vertices == LineString([original_edge_vertices.coords[1], original_edge_vertices.coords[0]]):
                        return polygon
        return None
    
    def _replace_edge(self, polygon, new_edge):
        """
        Replace the old edge with the new edge in the polygon.
        """
        new_edge_vertices = LineString([new_edge.coords[0], new_edge.coords[len(new_edge.coords) - 1]])
        new_edge_vertices_inv = LineString([new_edge.coords[len(new_edge.coords) - 1], new_edge.coords[0]])
        for i, edge in zip(range(len(polygon)), list(polygon)):
            edge_vertices = LineString([edge.coords[0], edge.coords[len(edge.coords) - 1]])
            if edge_vertices == new_edge_vertices or edge_vertices == new_edge_vertices_inv:
                polygon[i] = new_edge
                return polygon
        return None

    def _clean_edges(self):   
        for curved_poly in tqdm(list(self.curved_polygons), desc="Cleaning borders", unit="polygon"):
            for edge in list(curved_poly):
                if len(edge.coords) > 2:
                    # If the edge is a curve
                    edge_vertices = LineString([edge.coords[0], edge.coords[len(edge.coords) - 1]])
                    # We look for an adjacent polygon that shares the same edge in the cleaned_polygons list
                    adjacent_polygon = self._find_adjacent_polygon(self.cleaned_polygons, curved_poly, edge_vertices)
                    if adjacent_polygon is not None:
                        # If an adjacent polygon is found,
                        # We check if this polygon has already been updated (exists in cleaned_polygons)
                        new_polygon = self._replace_edge(adjacent_polygon, edge)
                        self.cleaned_polygons.remove(adjacent_polygon)
                        self.cleaned_polygons.append(new_polygon)
                    else:
                        # We look for an adjacent polygon in the curved_polygons list
                        adjacent_polygon = self._find_adjacent_polygon(self.curved_polygons, curved_poly, edge_vertices)
                        if adjacent_polygon is not None:
                            new_polygon = self._replace_edge(adjacent_polygon, edge)
                            self.cleaned_polygons.append(curved_poly)
                        else:
                            self.cleaned_polygons.append(curved_poly)
                else:
                    self.cleaned_polygons.append(curved_poly)
        print(f"Number of polygons after curving and cleaning borders: {len(self.curved_polygons)}")
        return self.cleaned_polygons

