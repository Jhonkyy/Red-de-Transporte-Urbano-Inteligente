from src.model.grafo import Grafo
from src.services.dijkstra import camino_corto
from src.model.ruta import Ruta

def sugerir_conexiones(grafo: Grafo, presupuesto: float):
    """
    Sugiere nuevas conexiones directas entre pares de estaciones donde el tiempo actual excede el presupuesto.
    Solo sugiere si la conexión directa reduciría el tiempo promedio entre estaciones.
    Retorna una lista de tuplas (origen, destino, tiempo_actual).
    """
    sugerencias = []
    estaciones = grafo.obtener_estaciones()
    for i, origen in enumerate(estaciones):
        for destino in estaciones:
            if origen == destino:
                continue
            # Verifica si ya existe una ruta directa
            if any(ruta.dest == destino for ruta in grafo.obtener_vecinos(origen)):
                continue
            camino, tiempo_actual = camino_corto(grafo, origen, destino)
            if tiempo_actual > presupuesto:
                # Simula agregar una conexión directa con peso igual al presupuesto
                grafo.añadir_ruta(Ruta(origen, destino, presupuesto))
                nuevo_camino, tiempo_nuevo = camino_corto(grafo, origen, destino)
                # Solo sugiere si el tiempo mejora
                if tiempo_nuevo < tiempo_actual:
                    sugerencias.append((origen, destino, tiempo_actual))
                # Quita la ruta simulada
                grafo.eliminar_ruta(Ruta(origen, destino, presupuesto))
    return sugerencias
