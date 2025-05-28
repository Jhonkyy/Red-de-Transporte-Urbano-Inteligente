"""
Módulo que implementa la detección de ciclos en la red de transporte urbano.
"""

from src.model.grafo import Grafo

def hay_ciclo(grafo: Grafo) -> bool:
    """
    Detecta ciclos en el grafo dirigido usando DFS (Depth-First Search).
    Retorna True si existe al menos un ciclo, False en caso contrario.
    """
    visitados = set()  # Conjunto de estaciones ya visitadas
    en_recursion = set()  # Conjunto de estaciones en el camino actual de DFS

    def dfs(estacion):
        visitados.add(estacion)
        en_recursion.add(estacion)
        # Recorre todos los vecinos de la estacion actual
        for ruta in grafo.obtener_vecinos(estacion):
            vecino = ruta.dest
            # Si el vecino no ha sido visitado, se aplica DFS sobre el
            if vecino not in visitados:
                if dfs(vecino):
                    return True
            # Si el vecino esta en el camino actual, se ha encontrado un ciclo
            elif vecino in en_recursion:
                return True
        en_recursion.remove(estacion)  # Se quita la estacion del camino actual
        return False

    # Se inicia el DFS desde cada estacion no visitada
    for estacion in grafo.obtener_estaciones():
        if estacion not in visitados:
            if dfs(estacion):
                return True
    return False
