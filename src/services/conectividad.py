from src.model.grafo import Grafo

def _alcanzables_desde(grafo: Grafo, inicio):
    visitados = set()
    stack = [inicio]
    while stack:
        actual = stack.pop()
        if actual not in visitados:
            visitados.add(actual)
            for ruta in grafo.obtener_vecinos(actual):
                stack.append(ruta.dest)
    return visitados

def es_fuertemente_conexo(grafo: Grafo) -> bool:
    estaciones = grafo.obtener_estaciones()
    for estacion in estaciones:
        alcanzados = _alcanzables_desde(grafo, estacion)
        if len(alcanzados) != len(estaciones):
            return False
    return True
