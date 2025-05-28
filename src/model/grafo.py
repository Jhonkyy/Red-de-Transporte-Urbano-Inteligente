"""
Módulo que define la clase Grafo para la red de transporte urbano.
"""

from src.model.estacion import Estacion
from src.model.ruta import Ruta


class Grafo:
    """
    Representa un grafo dirigido y ponderado para la red de transporte urbano.
    Permite agregar/eliminar estaciones y rutas, y cargar/guardar desde archivo.
    """

    def __init__(self):
        """
        Inicializa el grafo con listas de adyacencia y mapeo de nombres.
        """
        # Lista de adyacencia: Estacion -> lista de Rutas salientes
        self.adjlist: dict[Estacion, list[Ruta]] = {}
        # Mapeo rápido de nombre a objeto Estacion
        self.nombre_a_estacion = {}

    def añadir_estacion(self, estacion: Estacion):
        """
        Agrega una estación al grafo.
        """
        if estacion.nombre in self.nombre_a_estacion:
            raise Exception(f"la estacion {estacion} ya se encuentra en el grafo")
        else:
            self.adjlist[estacion] = []
            self.nombre_a_estacion[estacion.nombre] = estacion

    def añadir_ruta(self, ruta: Ruta):
        """
        Agrega una ruta dirigida entre dos estaciones.
        """
        if ruta.origen not in self.adjlist:
            raise Exception(f"No hay estacion {ruta.origen} en el grafo")
        if ruta.dest not in self.adjlist:
            raise Exception("No se encentra estacion destino")
        if ruta in self.adjlist[ruta.origen]:
            raise Exception("Ruta ya se encuentra en el grafo")
        else:
            self.adjlist[ruta.origen].append(ruta)

    def obtener_estaciones(self):
        """
        Devuelve una lista de todas las estaciones del grafo.
        """
        return list(self.adjlist.keys())

    def obtener_vecinos(self, estacion):
        """
        Devuelve una lista de rutas salientes desde la estación dada.
        """
        return self.adjlist[estacion]

    def encontrar_estacion(self, nombre: str) -> Estacion:
        """
        Busca y retorna la estación por su nombre.
        """
        return self.nombre_a_estacion[nombre]

    def eliminar_estacion(self, estacion: Estacion):
        """
        Elimina la estación y todas las rutas asociadas (entrantes y salientes).
        """
        if estacion not in self.adjlist:
            raise Exception(f"La estación {estacion} no existe en el grafo")
        # Elimina rutas que llegan a esta estación
        for rutas in self.adjlist.values():
            rutas[:] = [ruta for ruta in rutas if ruta.dest != estacion]
        # Elimina la estación
        del self.adjlist[estacion]
        del self.nombre_a_estacion[estacion.nombre]

    def eliminar_ruta(self, ruta: Ruta):
        """
        Elimina una ruta específica del grafo.
        """
        if ruta.origen not in self.adjlist:
            raise Exception(f"No existe la estación de origen {ruta.origen}")
        try:
            self.adjlist[ruta.origen].remove(ruta)
        except ValueError:
            raise Exception("La ruta no existe en el grafo")

    def cargar_desde_json(self, ruta_archivo):
        """
        Carga el grafo desde un archivo JSON con formato:
        {
            "estaciones": [nombres...],
            "rutas": [{"origen": ..., "destino": ..., "peso": ...}, ...]
        }
        """
        import json
        from src.model.estacion import Estacion
        from src.model.ruta import Ruta

        with open(ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        # Limpiar grafo actual
        self.adjlist.clear()
        self.nombre_a_estacion.clear()
        # Agregar estaciones
        for nombre in datos["estaciones"]:
            self.añadir_estacion(Estacion(nombre))
        # Agregar rutas
        for ruta in datos["rutas"]:
            origen = self.nombre_a_estacion[ruta["origen"]]
            destino = self.nombre_a_estacion[ruta["destino"]]
            peso = ruta["peso"]
            self.añadir_ruta(Ruta(origen, destino, peso))

    def guardar_a_json(self, ruta_archivo):
        """
        Guarda el grafo actual en un archivo JSON.
        """
        import json

        estaciones = [e.nombre for e in self.obtener_estaciones()]
        rutas = []
        for estacion in self.obtener_estaciones():
            for ruta in self.obtener_vecinos(estacion):
                rutas.append(
                    {
                        "origen": ruta.origen.nombre,
                        "destino": ruta.dest.nombre,
                        "peso": ruta.peso,
                    }
                )
        datos = {"estaciones": estaciones, "rutas": rutas}
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

