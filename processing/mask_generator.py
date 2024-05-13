from base_class import BaseClass
from PIL import Image

class MaskGenerator(BaseClass):
    def __init__(self, output_directory='masks/'):
        self.output_directory = output_directory

    def transform(self, png_file):
        # ... code to create masks from PNG file ...

    def display(self, masks):
        # ... code to display masks ...

    def save(self, masks, filename):
        # ... code to save masks ...

    def create_and_save_masks_from_png(self, png_file):
        masks = self.transform(png_file)
        self.display(masks)
        self.save(masks, self.output_directory + filename)