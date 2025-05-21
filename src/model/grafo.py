from src.model.estacion import Estacion
from src.model.ruta import Ruta


class Grafo:
    def __init__(self):
        self.adjlist: dict[Estacion, list[Ruta]] = {}

    def añadir_estacion(self, estacion: Estacion):
        self.adjlist[estacion] = []

    def añadir_ruta(self, ruta: Ruta):
        if ruta.origen not in self.adjlist:
            raise Exception (f"No hay estacion {ruta.origen} en el grafo")

        if ruta.dest not in self.adjlist:
            raise Exception ("No se encentra estacion destino")

        if ruta in self.adjlist[ruta.origen]:
            raise Exception ("Ruta ya se encuentra en el grafo")

        else:
            self.adjlist[ruta.origen].append(ruta)