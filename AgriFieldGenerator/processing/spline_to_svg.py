import re

from collections import OrderedDict
import numpy as np
import svgwrite

from .data_processor_base_class import DataProcessorBaseClass

class SplineToSVG(DataProcessorBaseClass):
    def __init__(self, svg_file_name, source_path, save_path, save_data_path, svg_height, svg_width, surface_map_resolution, enfusion_spline_layer_file):
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        self.source_path = source_path
        self.svg_file_name = source_path + svg_file_name
        self.source_layer = self.source_path + enfusion_spline_layer_file
        self.save_path = save_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.surface_map_resolution = surface_map_resolution
    
    def parse_spline_file(self):
        with open(self.source_layer, 'r') as file:
            content = file.readlines()
        splines = []  # List to store multiple splines
        spline = {"points": []}
        points = []
        current_point = OrderedDict()
        origin = np.array([0, 0, 0])  # Store the origin point
        for i, line in enumerate(content):
            if "SplineShapeEntity" in line:
                # If a spline already exists, add it to the list of splines
                if points:
                    spline['points'] = points
                    splines.append(spline)
                    points = []  # Reset the points list for the next spline
                # Initialize a new spline
                spline = {"points": [], "is_closed": 0}  # Default to not closed
            elif "IsClosed" in line:
                # Extract the IsClosed value
                is_closed = int(re.search(r'\d+', line).group())
                spline["is_closed"] = is_closed
            elif "coords" in line:
            # Extract the origin point coordinates
                origin_data = np.array([float(x) for x in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)])
                current_point["position"] = (origin_data).tolist()
                origin = np.array(origin_data)
                points.append(dict(current_point))
                current_point.clear()
            elif "Position" in line:
                # Extract the point coordinates
                position_data = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)]
                relative_position = np.array(position_data)
                # Convert to absolute coordinates by adding the origin
                absolute_position = (origin + relative_position)
                current_point["position"] = absolute_position.tolist()
                # Initialize in_tangent and out_tangent with current position if the next line does not contain 'Data'
                if i+1 < len(content) and "Data" not in content[i+1]:
                    current_point["in_tangent"] = [0, 0, 0]
                    current_point["out_tangent"] = [0, 0, 0]
            elif "InTangent" in line:
                relative_in_tangent = np.array([float(x) for x in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)])
                current_point["out_tangent"] = relative_in_tangent.tolist()
            elif "OutTangent" in line:
                relative_out_tangent = np.array([float(x) for x in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)])
                current_point["in_tangent"] = relative_out_tangent.tolist()
            # Add the current point to the list of points only if it has 'position', 'in_tangent' and 'out_tangent'
            if "position" in current_point and "in_tangent" in current_point and "out_tangent" in current_point:
                points.append(dict(current_point))
                current_point.clear()  # Reset the current point for the next one
        # Add the last spline to the list of splines
        if points:
            spline['points'] = points
            splines.append(spline)
        return splines

    def hermite_to_bezier(self, splines):
        
        dwg = svgwrite.Drawing(self.svg_file_name , profile='tiny', size=(self.svg_height, self.svg_width))      
        for spline in splines:
            points = spline['points'][1:]  # Exclude only the first point
            # Because we use this svg to generate surface masks, we have to divide the spline coordinates by the surface map resolution
            # to have the right scale betwwen map resolution and surface map resolution
            origin_coords = points[0]['position'][0] / self.surface_map_resolution, self.svg_height - (points[0]['position'][2] / self.surface_map_resolution)
            path = dwg.path(d=("M", origin_coords), fill='none', stroke='black')
            for i in range(len(points) - 1):
                p0 = [points[i]['position'][0] / self.surface_map_resolution, self.svg_height - (points[i]['position'][2] / self.surface_map_resolution)] 
                p1 = [p0[0] + points[i].get('in_tangent', [0, 0, 0])[0] / 3, p0[1] - points[i].get('in_tangent', [0, 0, 0])[2] / 3]
                p3 = [points[i+1]['position'][0] / self.surface_map_resolution, self.svg_height - (points[i+1]['position'][2] / self.surface_map_resolution)]
                p2 = [p3[0] - points[i+1].get('out_tangent', [0, 0, 0])[0] / 3, p3[1] + points[i+1].get('out_tangent', [0, 0, 0])[2] / 3]
                path.push("C", p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])

            # If the spline is closed, add a line from the last point to the first
            if spline["is_closed"]:
                p0 = [points[-1]['position'][0] / self.surface_map_resolution, self.svg_height - (points[-1]['position'][2] / self.surface_map_resolution)] 
                p3 = [points[0]['position'][0] / self.surface_map_resolution, self.svg_height - (points[0]['position'][2] / self.surface_map_resolution)]
                path.push("L", p3[0], p3[1])

            dwg.add(path)

        dwg.save()
        return self.svg_file_name


