import os

class BaseClass:
    def __init__(self, source_directory='work/source/', save_directory='work/save/'):
        self.source_directory = source_directory
        self.save_directory = save_directory

    def transform(self, input_data):
        raise NotImplementedError("Subclasses should implement this!")

    def display(self, result):
        raise NotImplementedError("Subclasses should implement this!")

    def save(self, result, filename):
        raise NotImplementedError("Subclasses should implement this!")

    def get_source_file_path(self, filename):
        return os.path.join(self.source_directory, filename)

    def get_save_file_path(self, filename):
        project_directory = os.path.join(self.save_directory, os.path.splitext(filename)[0])
        os.makedirs(project_directory, exist_ok=True)
        return os.path.join(project_directory, filename)