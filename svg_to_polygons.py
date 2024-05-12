from xml.dom.minidom import parse
from svg.path import parse_path, Line, CubicBezier, Move
from shapely.geometry import Polygon, MultiPolygon
import numpy as np
import matplotlib.pyplot as plt

def svg_file_to_polygon(svg_file, num_points=20, plot=False, mirror=False):
    dom = parse(svg_file)
    path_strings = [path.getAttribute('d') for path in dom.getElementsByTagName('path')]
    
    polygons = []
    for path_string in path_strings:
        path = parse_path(path_string)
        points = []
        for command in path:
            if isinstance(command, Line) or isinstance(command, CubicBezier):
                if isinstance(command, Line):
                    points.append((command.end.real, -command.end.imag if mirror else command.end.imag))
                else:  # CubicBezier
                    for t in np.linspace(0, 1, num=num_points):
                        point = command.point(t)
                        points.append((point.real, -point.imag if mirror else point.imag))
            elif isinstance(command, Move):
                if points and len(points) >= 4:  # Ensure there are at least 4 points
                    polygons.append(Polygon(points))
                    points = []  # Start a new polygon
                points.append((command.start.real, -command.start.imag if mirror else command.start.imag))

        if points and len(points) >= 4:  # Add the last polygon if it has at least 4 points
            polygons.append(Polygon(points))

    # Create a MultiPolygon from all the polygons
    multi_polygon = MultiPolygon(polygons)

    # Plot the polygons if requested
    if plot:
        fig, ax = plt.subplots()
        if isinstance(multi_polygon, MultiPolygon):
            for polygon in multi_polygon.geoms:
                x, y = polygon.exterior.xy
                ax.plot(x, y)
        elif isinstance(multi_polygon, Polygon):
            x, y = multi_polygon.exterior.xy
            ax.plot(x, y)
        plt.show()

    return multi_polygon