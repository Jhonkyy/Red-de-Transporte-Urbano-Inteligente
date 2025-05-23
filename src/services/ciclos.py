from src.model.grafo import Grafo

def hay_ciclo(grafo: Grafo) -> bool:
    visitados = set()
    en_recursion = set()

    def dfs(estacion):
        visitados.add(estacion)
        en_recursion.add(estacion)
        for ruta in grafo.obtener_vecinos(estacion):
            vecino = ruta.dest
            if vecino not in visitados:
                if dfs(vecino):
                    return True
            elif vecino in en_recursion:
                return True
        en_recursion.remove(estacion)
        return False

    for estacion in grafo.obtener_estaciones():
        if estacion not in visitados:
            if dfs(estacion):
                return True
    return False
