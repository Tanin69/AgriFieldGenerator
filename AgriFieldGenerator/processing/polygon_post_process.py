import random

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString
from tqdm import tqdm


class PolygonPostProcess():
    def __init__(self):
        self.polygons = []
        self.curved_polygons = []
        self.cleaned_polygons = []
        self.svg_width = 500
        self.svg_height = 500

    def generate_polygon_tiles(self, nx, ny, size=1):
        for i in range(nx):
            for j in range(ny):
                self.polygons.append(Polygon([(i*size, j*size), ((i+1)*size, j*size), ((i+1)*size, (j+1)*size), (i*size, (j+1)*size)]))
        return self.polygons

    def pp_curve_voronoi_edges(self, curve_probability=0.1):
        print(f"Nombre de polygones avant transformation : {len(self.polygons)}")
        for polygon in self.polygons:
            if isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    self.curved_polygons.append(self._curve_polygon_edges_random(poly, curve_probability))
            else:
                self.curved_polygons.append(self._curve_polygon_edges_random(polygon, curve_probability))
        # self.polygons = self.curved_polygons
        print(f"Nombre de polygones après transformation : {len(self.curved_polygons)}")
        # Save the data and return the voronoi polygons
        # print(self.curved_polygons)
        return self.curved_polygons

    def clean_edges(self):
   
        for curved_poly in tqdm(list(self.curved_polygons), desc="Nettoyage des arêtes", unit="polygones"):
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
        print(f"Nombre de polygones après nettoyage : {len(self.curved_polygons)}")
        return self.cleaned_polygons

    def _curve_polygon_edges_random(self, polygon, curve_probability):
        # curved_polygon_points = []
        curved_polygon_edges = []

        # Iterate over the edges of the polygon
        for i in range(len(polygon.exterior.coords) - 1):
            start_point, end_point = polygon.exterior.coords[i], polygon.exterior.coords[i+1]
            old_edge = LineString([start_point, end_point])
            if random.uniform(0, 1) < curve_probability:  # the edge is a line, curve it with a certain probability
                control_points = self._generate_control_points(start_point, end_point, 20)
                new_edge = self._generate_pseudo_curve(start_point, control_points, end_point)
            else:  # the edge is a line and we don't curve it
                new_edge = old_edge

            # Add the new edge to the resulting polygon
            curved_polygon_edges.append(new_edge)
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
    
    def display(self):
        plt.figure()      
        for polygon in self.cleaned_polygons:
            for line in polygon:
                x, y = line.xy
                plt.plot(x, y)
        plt.show()

if __name__ == "__main__":
    pp = PolygonPostProcess()
    pp.generate_polygon_tiles(20, 20, 10)
    pp.pp_curve_voronoi_edges(0.2)
    pp.clean_edges()
    pp.display()