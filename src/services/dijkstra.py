from src.model.estacion import Estacion
from src.model.grafo import Grafo


def camino_corto(grafo: Grafo, inicio: Estacion, destino: Estacion):
    visitados = set()
    distances = {node: float("inf") for node in grafo.obtener_estaciones()}
    anterior = {node: None for node in grafo.obtener_estaciones()}
    distances[inicio] = 0

    while len(visitados) != len(grafo.obtener_estaciones()):
        min_node = None
        min_dis = float("inf")

        for node in grafo.obtener_estaciones():
            if node not in visitados and distances[node] < min_dis:
                min_dis = distances[node]
                min_node = node

        current = min_node
        if min_node is None:
            break

        for vecino in grafo.obtener_vecinos(current):
            peso = vecino.peso
            nodo_vecino = vecino.dest
            tentativa = distances[current] + peso

            if tentativa < distances[nodo_vecino] and nodo_vecino not in visitados:
                distances[nodo_vecino] = tentativa
                anterior[nodo_vecino] = current

        visitados.add(current)

    # Reconstruir el camino óptimo
    camino = []
    actual = destino
    while actual is not None:
        camino.insert(0, actual)
        actual = anterior[actual]
    if distances[destino] == float("inf"):
        return None, float("inf")  # No hay camino
    return camino, distances[destino]
