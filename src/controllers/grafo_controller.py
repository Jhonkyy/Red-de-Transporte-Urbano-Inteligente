from src.model.grafo import Grafo
from src.model.estacion import Estacion
from src.model.ruta import Ruta

def agregar_estacion(grafo: Grafo, nombre: str):
    estacion = Estacion(nombre)
    grafo.añadir_estacion(estacion)
    return estacion

def eliminar_estacion(grafo: Grafo, nombre: str):
    estacion = grafo.encontrar_estacion(nombre)
    grafo.eliminar_estacion(estacion)

def agregar_ruta(grafo: Grafo, origen_nombre: str, destino_nombre: str, peso: float):
    origen = grafo.encontrar_estacion(origen_nombre)
    destino = grafo.encontrar_estacion(destino_nombre)
    ruta = Ruta(origen, destino, peso)
    grafo.añadir_ruta(ruta)
    return ruta

def eliminar_ruta(grafo: Grafo, origen_nombre: str, destino_nombre: str):
    origen = grafo.encontrar_estacion(origen_nombre)
    destino = grafo.encontrar_estacion(destino_nombre)
    rutas = [ruta for ruta in grafo.obtener_vecinos(origen) if ruta.dest == destino]
    for ruta in rutas:
        grafo.eliminar_ruta(ruta)
