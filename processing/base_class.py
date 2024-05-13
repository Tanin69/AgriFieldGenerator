class BaseClass:
    def transform(self, input_data):
        raise NotImplementedError("Subclasses should implement this!")

    def display(self, result):
        raise NotImplementedError("Subclasses should implement this!")

    def save(self, result, filename):
        raise NotImplementedError("Subclasses should implement this!")