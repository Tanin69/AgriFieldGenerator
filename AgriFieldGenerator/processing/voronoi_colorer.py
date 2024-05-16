import matplotlib.pyplot as plt
import networkx as nx
from random import choice, uniform
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry import Polygon as ShapelyPolygon

from .data_processor_base_class import DataProcessorBaseClass

class ColoredPolygon:
    def __init__(self, coords, color=None, border_width=None):
        self.polygon = ShapelyPolygon(coords)
        self.color = color
        self.border_width = border_width

class VoronoiColorer(DataProcessorBaseClass):
    def __init__(self,
                source_path,
                save_path,
                save_data_path,
                svg_height,
                svg_width,
                min_border_width=0.1,
                max_border_width=2):
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.min_border_width = min_border_width
        self.max_border_width = max_border_width
        self.colored_polygons = None

        try:
            # Load needed data
            self.polygon = self.load('polygon.pkl', data_file=True)
            self.points = self.load('points.pkl', data_file=True)
            self.intersection_polygons = self.load('voronoi.pkl', data_file=True)
        except FileNotFoundError:
            raise FileNotFoundError("Polygon, points or Voronoi diagram data are missing. Please run the SvgToPolygon, PointsGenerator and VoronoiFiller classes first!")
    
    def process(self):

        # Create a list to store the colored polygons
        self.colored_polygons = []

        # Create a graph
        G = nx.Graph()

        # Add nodes to the graph
        for i, poly in enumerate(self.intersection_polygons):
            G.add_node(i)

        # Add edges to the graph
        for i, poly1 in enumerate(self.intersection_polygons):
            for j, poly2 in enumerate(self.intersection_polygons):
                if i != j and poly1.touches(poly2):
                    G.add_edge(i, j)

        # Color the graph
        color_map = nx.greedy_color(G, strategy=nx.coloring.strategy_connected_sequential_bfs)

        # Define a color palette with 4 shades of gray
        palette = ['#000000', '#555555', '#AAAAAA', '#DDDDDD']

        # Color the polygons
        for i, poly in enumerate(self.intersection_polygons):
            color = palette[color_map[i] % len(palette)]  # Get the color from the palette
            if isinstance(poly, Polygon):
                x, y = poly.exterior.xy
                border_width = uniform(self.min_border_width, self.max_border_width) if self.max_border_width > self.min_border_width else self.min_border_width
                colored_polygon = ColoredPolygon(zip(x, y), color=color, border_width=border_width)
                self.colored_polygons.append(colored_polygon)  # Add the colored polygon to the list
            elif isinstance(poly, MultiPolygon):
                for sub_poly in poly.geoms:
                    x, y = sub_poly.exterior.xy
                    border_width = uniform(self.min_border_width, self.max_border_width) if self.max_border_width > self.min_border_width else self.min_border_width
                    colored_polygon = ColoredPolygon(zip(x, y), color=color, border_width=border_width)
                    self.colored_polygons.append(colored_polygon)  # Add the colored polygon to the list
              
        # Color the non-colored areas
        colored_area = unary_union([cp.polygon for cp in self.colored_polygons])

        # Subtract the colored area from the total area to get the non-colored area
        total_area = unary_union(self.polygon)
        non_colored_area = total_area.difference(colored_area)

        # If the non-colored area is a Polygon, make it into a list
        if isinstance(non_colored_area, Polygon):
            non_colored_area = [non_colored_area]
        elif isinstance(non_colored_area, MultiPolygon):
            non_colored_area = list(non_colored_area.geoms)

        # Color each non-colored area with a random color from the palette
        for area in non_colored_area:
            color = choice(palette)
            x, y = area.exterior.xy
            if self.max_border_width > self.min_border_width:
                border_width = uniform(self.min_border_width, self.max_border_width)
            colored_polygon = ColoredPolygon(zip(x, y), color=color, border_width=border_width)
            # Add the colored polygon to self.colored_polygons
            self.colored_polygons.append(colored_polygon)    

        # Save the data and return the colored polygons
        self.save(self.colored_polygons, 'colored.pkl', data_file=True)
        return self.colored_polygons
    
    def display(self):
            
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
        for point in self.points:
            ax.plot(*point, 'ko', markersize=1)
            
        for polygon in self.intersection_polygons:
            if isinstance(polygon, Polygon):
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='b')
            elif isinstance(polygon, MultiPolygon):
                for poly in polygon.geoms:
                    x, y = poly.exterior.xy
                    ax.plot(x, y, color='b')

        if self.colored_polygons is None:
            print("Error: self.colored_polygons is None. You need to generate the colored Voronoi first by calling the process() method.")
            return
        # Display colored polygons
        for colored_polygon in self.colored_polygons:
            if isinstance(colored_polygon, ColoredPolygon):
                x, y = colored_polygon.polygon.exterior.xy
                ax.fill(x, y, color=colored_polygon.color)
            elif isinstance(colored_polygon, MultiPolygon):
                for poly in colored_polygon.polygon.geoms:
                    x, y = poly.exterior.xy
                    ax.fill(x, y, color=colored_polygon.color)
        
        plt.show()
