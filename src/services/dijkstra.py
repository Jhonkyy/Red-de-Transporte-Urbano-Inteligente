"""
Módulo que implementa el algoritmo de Dijkstra para la red de transporte urbano.
"""

from src.model.estacion import Estacion
from src.model.grafo import Grafo
import heapq


def camino_corto(grafo: Grafo, inicio: Estacion, destino: Estacion):
    """
    Calcula la ruta más corta entre dos estaciones usando Dijkstra.
    Devuelve una tupla (camino, tiempo_total).
    - camino: lista de estaciones desde inicio hasta destino (incluidos).
    - tiempo_total: suma de los pesos de la ruta óptima.
    Si no hay camino, retorna (None, float('inf')).
    """
    # Inicialización de distancias y predecesores
    distances = {node: float("inf") for node in grafo.obtener_estaciones()}
    anterior = {node: None for node in grafo.obtener_estaciones()}
    distances[inicio] = 0
    visitados = set()
    # El heap ahora incluye el nombre como "tie-breaker"
    heap = [(0, inicio.nombre, inicio)]

    while heap:
        distancia_actual, _, current = heapq.heappop(heap)
        if current in visitados:
            continue
        visitados.add(current)
        if current == destino:
            break
        for vecino in grafo.obtener_vecinos(current):
            peso = vecino.peso
            nodo_vecino = vecino.dest
            tentativa = distances[current] + peso
            if tentativa < distances[nodo_vecino]:
                distances[nodo_vecino] = tentativa
                anterior[nodo_vecino] = current
                heapq.heappush(heap, (tentativa, nodo_vecino.nombre, nodo_vecino))

    # Reconstruir el camino óptimo
    camino = []
    actual = destino
    while actual is not None:
        camino.insert(0, actual)
        actual = anterior[actual]
    if distances[destino] == float("inf"):
        return None, float("inf")  # No hay camino
    return camino, distances[destino]
