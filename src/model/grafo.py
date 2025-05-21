from src.model.estacion import Estacion
from src.model.ruta import Ruta


class Grafo:
    def __init__(self):
        self.adjlist: dict[Estacion, Ruta] = {}