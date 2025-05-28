"""
Módulo que define la clase Ruta para la red de transporte urbano.
"""

from src.model.estacion import Estacion


class Ruta:
    """
    Representa una ruta dirigida y ponderada entre dos estaciones.
    """

    def __init__(self, origen: Estacion, dest: Estacion, peso: float = 1):
        """
        Inicializa una ruta con origen, destino y peso (tiempo).
        """
        self.origen = origen
        self.dest = dest
        self.peso = peso

    def __eq__(self, other):
        """
        Compara dos rutas por origen, destino y peso.
        """
        if not isinstance(other, Ruta):
            return False
        return (
            self.origen == other.origen
            and self.dest == other.dest
            and self.peso == other.peso
        )

    def __hash__(self):
        """
        Permite usar Ruta como clave en diccionarios y sets.
        """
        return hash((self.origen, self.dest, self.peso))

