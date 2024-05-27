import cv2
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, MultiPolygon
import pickle

from .enfusion_utils import EnfusionUtils

class PolylineGenerator:
    def __init__(self, svg_height, save_path, save_data_path):
        self.svg_height = svg_height
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.colored_polygon = save_data_path + 'colored.pkl'
        self.enfusion_utils = EnfusionUtils()

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
        
        enfusion_utils = EnfusionUtils()
        polylines = []
        # We need to define an offset because of the surface resolution in Enfusion: terrain coordinates and surface mask coordinates are not the same
        offset = 1.0079
        
        for poly in self.polygon:
            x, y = poly.polygon.exterior.xy
            origin = (x[0] * offset, 0, y[0] * offset)
            relative_points = [((x[i] * offset) - origin[0], 0, (y[i] * offset) - (origin[2])) for i in range(1, len(x))]
            polyline = enfusion_utils.generate_enfusion_polyline(origin, relative_points)
            polylines.append(polyline)

        # Save the polylines to a file
        with open(self.save_path + 'polylines_colored.layer', 'w') as f:
            f.write('\n'.join(polylines))
     
        return polylines

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