import random

class EnfusionUtils():
    def __init__(self):
        pass

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
