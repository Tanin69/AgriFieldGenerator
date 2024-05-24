# Cette classe génère des entités Enfusion pour pouvoir les placer dans le monde.
# Elle génère des entités de type Bushlines, Bushes, Trees, Rocks.
# Pour cela, elle convertit des polylines en entités polylines codées au format Enfusion.
# Les polylines sont générées à partir du fichier voronoi.pkl qui contient les polygones de Voronoi.
# Dans Enfusion, les layers sont stockés dans un fichier .layer.
# Chaque layer sur lequel nous allons travailler contient des entités de type polylines
# La structure d'un tel layer est la suivante:

#PolylineShapeEntity {
# coords 13483.974 49.563 10852.328
# Points {
#  ShapePoint "{616C606ECBF07F54}" {
#   Position 0 -0.001 0
#  }
#  ShapePoint "{616C606ECBF02835}" {
#   Position 54.939 -0.001 22.584
#  }
#  ShapePoint "{616C606EC6E64EE6}" {
#   Position 111.907 0.001 12.167
#  }
#  ShapePoint "{616C606EC7F3DF46}" {
#   Position 119.026 0.001 -13.614
#  }
#  ShapePoint "{616C606EC4F33F76}" {
#   Position 204.852 -0.001 21.232
#  }
# }
#}
# coords sont les coordonnées du premier point de la polyline dans un système de coordonnées global.
# Points sont les points de la polyline. Chaque point est défini par un ShapePoint.
# Position est la position du point par rapport au point d'origine de la polyline.

# Nous allons d'abord écrire une fonction qui génère une entité de type polylines pour chaque polygone de Voronoi.

import random

class EnfusionUtils():
    def __init__(self):
        pass

    def generate_enfusion_polyline(self, origin, points):
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

        # Print the entity string to the console
        print(entity_str)

        return entity_str

    def _generate_random_id(self):
        """
        Generate a random ID for a ShapePoint.
        :return: A random ID as a string.
        """
        return "{%016X}" % random.randint(0, 2**64-1)
