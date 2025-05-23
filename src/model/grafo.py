from src.model.estacion import Estacion
from src.model.ruta import Ruta


class Grafo:
    def __init__(self):
        self.adjlist: dict[Estacion, list[Ruta]] = {}
        self.nombre_a_estacion = {}

    def añadir_estacion(self, estacion: Estacion):
        if estacion.nombre in self.nombre_a_estacion:
            raise Exception (f"la estacion {estacion} ya se encuentra en el grafo")
        else:
            self.adjlist[estacion] = []
            self.nombre_a_estacion[estacion.nombre] = estacion

    def añadir_ruta(self, ruta: Ruta):
        if ruta.origen not in self.adjlist:
            raise Exception (f"No hay estacion {ruta.origen} en el grafo")

        if ruta.dest not in self.adjlist:
            raise Exception ("No se encentra estacion destino")

        if ruta in self.adjlist[ruta.origen]:
            raise Exception ("Ruta ya se encuentra en el grafo")

        else:
            self.adjlist[ruta.origen].append(ruta)

    def obtener_estaciones(self):
        return list(self.adjlist.keys())

    def obtener_vecinos(self, estacion):
        return self.adjlist[estacion]

    def encontrar_estacion(self, nombre: str) -> Estacion:
        return self.nombre_a_estacion[nombre]

    def eliminar_estacion(self, estacion: Estacion):
        # Elimina la estación y todas las rutas asociadas
        if estacion not in self.adjlist:
            raise Exception(f"La estación {estacion} no existe en el grafo")
        # Elimina rutas que llegan a esta estación
        for rutas in self.adjlist.values():
            rutas[:] = [ruta for ruta in rutas if ruta.dest != estacion]
        # Elimina la estación
        del self.adjlist[estacion]
        del self.nombre_a_estacion[estacion.nombre]

    def eliminar_ruta(self, ruta: Ruta):
        # Elimina una ruta específica
        if ruta.origen not in self.adjlist:
            raise Exception(f"No existe la estación de origen {ruta.origen}")
        try:
            self.adjlist[ruta.origen].remove(ruta)
        except ValueError:
            raise Exception("La ruta no existe en el grafo")

