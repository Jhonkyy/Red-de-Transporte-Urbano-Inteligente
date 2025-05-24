from src.model.grafo import Grafo
from src.services.dijkstra import camino_corto

def sugerir_conexiones(grafo: Grafo, presupuesto: float):
    sugerencias = []
    estaciones = grafo.obtener_estaciones()
    for i, origen in enumerate(estaciones):
        for destino in estaciones[i+1:]:
            # Verifica si ya existe una ruta directa
            if not any(ruta.dest == destino for ruta in grafo.obtener_vecinos(origen)):
                camino, tiempo_actual = camino_corto(grafo, origen, destino)
                # Si el tiempo actual es mayor que el presupuesto, sugerir conexión directa
                if tiempo_actual > presupuesto:
                    sugerencias.append((origen, destino, tiempo_actual))
            # También verifica en sentido inverso
            if not any(ruta.dest == origen for ruta in grafo.obtener_vecinos(destino)):
                camino, tiempo_actual = camino_corto(grafo, destino, origen)
                if tiempo_actual > presupuesto:
                    sugerencias.append((destino, origen, tiempo_actual))
    return sugerencias
