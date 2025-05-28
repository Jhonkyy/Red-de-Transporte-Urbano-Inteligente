"""
Módulo que define la clase Estacion para la red de transporte urbano.
"""

class Estacion:
    """
    Representa una estación o parada en la red de transporte.
    """

    def __init__(self, nombre: str):
        """
        Inicializa una estación con su nombre.
        """
        self.nombre = nombre

    def __str__(self):
        """
        Devuelve el nombre de la estación como string.
        """
        return self.nombre

    def __repr__(self):
        """
        Representación de la estación para depuración.
        """
        return self.nombre

    def __eq__(self, other):
        """
        Compara dos estaciones por su nombre.
        """
        return isinstance(other, Estacion) and self.nombre == other.nombre

    def __hash__(self):
        """
        Permite usar Estacion como clave en diccionarios y sets.
        """
        return hash(self.nombre)