from .data_processor_base_class import DataProcessorBaseClass

class MaskGenerator(DataProcessorBaseClass):
    def __init__(self, output_directory='masks/'):
        self.output_directory = output_directory

    def process(self, png_file):
        pass

    def display(self, masks):
        pass

    def save(self, masks, filename):
        pass

    def create_and_save_masks_from_png(self, png_file):
        pass