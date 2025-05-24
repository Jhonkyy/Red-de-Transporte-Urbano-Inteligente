from src.model.grafo import Grafo

def actualizar_peso_ruta(grafo: Grafo, origen_nombre: str, destino_nombre: str, nuevo_peso: float):
    origen = grafo.encontrar_estacion(origen_nombre)
    destino = grafo.encontrar_estacion(destino_nombre)
    for ruta in grafo.obtener_vecinos(origen):
        if ruta.dest == destino:
            ruta.peso = nuevo_peso
            return True
    return False  # No se encontró la ruta
