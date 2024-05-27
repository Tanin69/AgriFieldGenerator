import random

import cv2
import numpy as np
from PIL import Image
import pickle

class PolylineGenerator:
    def __init__(self, surface_map_resolution, save_path, save_data_path):
        self.surface_map_resolution = surface_map_resolution
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.colored_polygon = save_data_path + 'colored.pkl'

    def generate_polylines(self):
        """
        Generates a polyline for the border of a colored polygon.

        Parameters
        ----------
        None

        Returns
        -------
        polyline : Polyline
            The generated polyline.
        """

        with open(self.colored_polygon, 'rb') as f:
            self.polygon = pickle.load(f)
        
        polylines = []
        # We need to define an offset because of the surface resolution in Enfusion: terrain coordinates and surface mask coordinates are not the same
        offset = self.surface_map_resolution
        
        for poly in self.polygon:
            x, y = poly.polygon.exterior.xy
            origin = (x[0] * offset, 0, y[0] * offset)
            relative_points = [((x[i] * offset) - origin[0], 0, (y[i] * offset) - (origin[2])) for i in range(1, len(x))]
            polyline = self._generate_enfusion_polyline(origin, relative_points)
            polylines.append(polyline)

        # Save the polylines to a file
        with open(self.save_path + 'polylines_colored.layer', 'w') as f:
            f.write('\n'.join(polylines))

        print(f"Generated {len(polylines)} Enfusion polylines for colored polygons (see 'polylines_colored.layer' in the saves directory).")
     
        return polylines
    
    def _generate_enfusion_polyline(self, origin, points):
        """
        Generate a polyline entity in Enfusion format.
        :param origin: The origin point coordinates as a tuple (x, y, z).
        :param points: A list of point coordinates relative to the origin, each as a tuple (x, y, z).
        :return: A string representing the polyline entity in Enfusion format.
        """
        entity = []

        # Add the PolylineShapeEntity with origin coords
        entity.append('PolylineShapeEntity {')
        entity.append(' coords {0} {1} {2}'.format(*origin))

        entity.append(' Points {')

        # Add the origin point
        entity.append('  ShapePoint "{0}" {{'.format(self._generate_random_id()))
        entity.append('   Position 0 0 0')
        entity.append('  }')

        # Add the relative points
        for point in points:
            entity.append('  ShapePoint "{0}" {{'.format(self._generate_random_id()))
            entity.append('   Position {0} {1} {2}'.format(*point))
            entity.append('  }')

        entity.append(' }')
        entity.append('}')

        # Join the entity lines into a single string
        entity_str = '\n'.join(entity)

        return entity_str

    def _generate_random_id(self):
        """
        Generate a random ID for a ShapePoint.
        :return: A random ID as a string.
        """
        return "{%016X}" % random.randint(0, 2**64-1)

        img = Image.open(self.image_path)
        data = np.array(img)
        x_offset = 28
        y_offset = 28 # Sort of magic value ;-)
        enfusion_polylines = []

        black_color = (0, 0, 0)  # RGB for black
        mask = np.all(data[:, :, :3] == black_color, axis=-1)  # Only use the first three channels (RGB)

        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polylines = [cv2.approxPolyDP(contour, 1, False) for contour in contours]

        for polyline in polylines:
            origin = (polyline[0][0][0] + x_offset, 0, (self.svg_height - polyline[0][0][1]) + y_offset)  # Add z coordinate
            points = [(point[0][0] - (origin[0] - x_offset), 0, (self.svg_height - point[0][1])- (origin[2] - y_offset)) for point in polyline[1:]]  # Add z coordinate
            enfusion_polyline = self.enfusion_utils.generate_enfusion_polyline(origin, points)
            enfusion_polylines.append(enfusion_polyline)

        with open(self.save_path + 'polylines_cv2.layer', 'w') as f:
            f.write('\n'.join(enfusion_polylines))

        return enfusion_polylines