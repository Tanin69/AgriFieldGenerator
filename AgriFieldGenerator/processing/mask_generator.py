from .data_processing_base_class import DataProcessingBaseClass

class MaskGenerator(DataProcessingBaseClass):
    def __init__(self, output_directory='masks/'):
        self.output_directory = output_directory

    def transform(self, png_file):
        pass

    def display(self, masks):
        pass

    def save(self, masks, filename):
        pass

    def create_and_save_masks_from_png(self, png_file):
        pass