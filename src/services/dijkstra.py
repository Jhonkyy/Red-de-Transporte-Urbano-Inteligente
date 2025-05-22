from src.model.estacion import Estacion
from src.model.grafo import Grafo


def camino_corto(grafo: Grafo, inicio: Estacion)-> dict:
    visitados = set()
    distances = {node: float("inf") for node in grafo.obtener_estaciones()}
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
            peso = vecino[1]
            nodo_vecino = vecino[0]
            tentativa = distances[current] + peso

            if tentativa < distances[nodo_vecino] and nodo_vecino not in visitados:
                distances[nodo_vecino] = tentativa

        visitados.add(current)

    return distances
