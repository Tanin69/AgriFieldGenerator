import numpy as np
from PIL import Image
from rasterio import features
from shapely.geometry import Polygon

from .data_processor_base_class import DataProcessorBaseClass

class MaskGenerator(DataProcessorBaseClass):
    def __init__(self,
            source_path,
            save_path,
            save_data_path,
            svg_height,
            svg_width,
            min_border_width=0.1,
            max_border_width=5):
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path)
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.svg_height = svg_height
        self.svg_width = svg_width
        self.min_border_width = min_border_width
        self.max_border_width = max_border_width
        self.colored_polygons = None

    def process(self):
        # Define your fixed color palette
        palette = ['#3a3e23', '#876d3a', '#76724d', '#362921']

        # Load the image from the file saved by VoronoiColorer
        img = Image.open(f'{self.save_path}/preview.png')
        data = np.array(img)

        # For each color in the palette
        for color in palette:
            # Remove the '#' from the color string
            color = color.lstrip('#')

            # Convert the color to RGB format
            rgb_color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

            # Create a mask with the same shape as the image data
            mask = np.all(data[:, :, :3] == rgb_color, axis=-1)  # Only use the first three channels (RGB)

            # Convert the mask to an image
            mask_img = Image.fromarray(mask.astype('uint8') * 255)

            # Save the mask image to a new PNG file
            mask_img.save(f'{self.save_path}/mask_{color}.png')

    def display(self, masks):
        pass

