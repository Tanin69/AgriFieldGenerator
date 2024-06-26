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

import cv2  
import numpy as np
from PIL import Image
from tqdm import tqdm

from .data_processor_base_class import DataProcessorBaseClass

# palette : 
#  Crop_Field_01.jpg
#  Crop_Field_02.jpg
#  ZI_Crop_Field_03.jpg
#  Grass_02.jpg

class MaskGenerator(DataProcessorBaseClass):
    """
    A class used to generate masks for different colors in an image.

    Attributes
    ----------
    source_path : str
        The path to the source file.
    save_path : str
        The path where the result will be saved.
    save_data_path : str
        The path where the data will be saved.
    svg_height : int
        The height of the SVG.
    svg_width : int
        The width of the SVG.
    palette : list
        The color palette to use for coloring.
    enfusion_texture_masks : dict
        A dictionary containing the Enfusion texture masks.
    min_border_width : float
        The minimum border width.
    max_border_width : float
        The maximum border width.
    colored_polygons : list
        A list of ColoredPolygon objects.
    """
    def __init__(self,
            source_path,
            save_path,
            save_data_path,
            svg_path,
            svg_height,
            svg_width,
            palette,
            enfusion_texture_masks,
            min_border_width=0.1,
            max_border_width=5):
        """
        Constructs all the necessary attributes for the MaskGenerator object.

        Parameters
        ----------
        source_path : str
            The path to the source file.
        save_path : str
            The path where the result will be saved.
        save_data_path : str
            The path where the data will be saved.
        svg_height : int
            The height of the SVG.
        svg_width : int
            The width of the SVG.
        palette : list
            The color palette to use for coloring.
        enfusion_texture_masks : dict
            A dictionary containing the Enfusion texture masks.
        min_border_width : float
            The minimum border width.
        max_border_width : float
            The maximum border width.
        """
        super().__init__(source_path=source_path, save_path=save_path, save_data_path=save_data_path, svg_path=svg_path, svg_height=svg_height, svg_width=svg_width)
        self.source_path = source_path
        self.save_path = save_path
        self.save_data_path = save_data_path
        self.palette = palette
        self.enfusion_texture_masks = enfusion_texture_masks
        self.min_border_width = min_border_width
        self.max_border_width = max_border_width
        self.colored_polygons = None

    def process(self):
        """
        Processes the image and generates masks for each color in the palette.

        The masks are saved as PNG files in the save path.
        """
        # Define your fixed color palette
        palette = self.palette

        # Load the image from the file saved by VoronoiColorer
        img = Image.open(f'{self.save_path}/preview.png')
        data = np.array(img)

        # For each color in the palette
        description = "Generating masks"
        description += " " * (26 - len(description))
        for i, color in tqdm(enumerate(palette), desc=description, total=len(palette), unit=" step"):
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

    def merge_masks(self, reset=True):
        """
        Merges the generated masks with external masks.

        Parameters
        ----------
        reset : bool, optional
            Whether to reset the external masks before merging (default is True).

        The merged masks are saved as PNG files in the save path.
        """
        if self.enfusion_texture_masks is None:
            return
    
        # Get the list of external mask files
        external_mask_files = [file for key, file in self.enfusion_texture_masks.items() if key != "etm_path"]
    
        # For each color in the palette
        description = "Merging masks"
        description += " " * (26 - len(description))
        for i, color in tqdm(enumerate(self.palette), desc=description, total=len(self.palette), unit=" step"):
        # Remove the '#' from the color string
            color = color.lstrip('#')
        
            # Load the mask generated by the process method
            mask_img = Image.open(f'{self.save_path}/mask_{color}.png')
            mask = np.array(mask_img)
        
           # If there is an external mask file for this color
            if i < len(external_mask_files):
                # Load the external mask
                external_mask_file = external_mask_files[i]
                external_mask_img = Image.open(f'{self.enfusion_texture_masks["etm_path"]}/{external_mask_file}')
                external_mask = np.array(external_mask_img)

                if reset:
                    # Load the polygon from the pickle file
                    multipolygon = self.load('polygon.pkl', data_file=True)

                    # Iterate over the polygons in the MultiPolygon
                    for polygon in multipolygon.geoms:
                        # Convert the polygon points to integer
                        polygon = np.round(np.array(polygon.exterior.coords)).astype(int)

                        # Correct the y coordinates
                        polygon[:, 1] = self.svg_height - polygon[:, 1]

                        # Reshape the polygon to meet the requirements of cv2.fillPoly()
                        polygon = polygon.reshape((-1, 1, 2))

                        # Draw a black polygon on the external mask
                        cv2.fillPoly(external_mask, [polygon], color=0)

                # Merge the masks
                mask = np.where((mask > 0) & (external_mask != 255), 255, external_mask)

                # Convert the merged mask to an image
                merged_mask_img = Image.fromarray(mask.astype('uint8'))

                # Get the base name of the external mask file (without the directory path and extension)
                external_mask_basename, extension = os.path.splitext(os.path.basename(external_mask_file))

                # Save the merged mask image to a new PNG file, named after the external mask with the new suffix
                merged_mask_img.save(f'{self.save_path}/{external_mask_basename}_AFG_merged{extension}')
                

