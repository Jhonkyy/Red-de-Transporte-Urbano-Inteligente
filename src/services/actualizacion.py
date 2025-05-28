from src.model.grafo import Grafo
import random

def actualizar_peso_ruta(grafo: Grafo, origen_nombre: str, destino_nombre: str, nuevo_peso: float):
    """
    Actualiza el peso de una ruta específica entre dos estaciones.

    :param grafo: El grafo que contiene las estaciones y rutas.
    :param origen_nombre: El nombre de la estación de origen.
    :param destino_nombre: El nombre de la estación de destino.
    :param nuevo_peso: El nuevo peso a asignar a la ruta.
    :return: True si se actualizó el peso, False si no se encontró la ruta.
    """
    origen = grafo.encontrar_estacion(origen_nombre)
    destino = grafo.encontrar_estacion(destino_nombre)
    for ruta in grafo.obtener_vecinos(origen):
        if ruta.dest == destino:
            ruta.peso = nuevo_peso
            return True
    return False  # No se encontró la ruta

def simular_congestion(grafo: Grafo, factor_min=1.2, factor_max=2.0, porcentaje=0.3):
    """
    Simula la congestión en el grafo aumentando aleatoriamente los pesos de un porcentaje de rutas.

    :param grafo: El grafo que contiene las estaciones y rutas.
    :param factor_min: El factor mínimo por el cual multiplicar el peso de la ruta.
    :param factor_max: El factor máximo por el cual multiplicar el peso de la ruta.
    :param porcentaje: El porcentaje de rutas a las que se les aplicará la congestión.
    :return: Una lista de tuplas con la información de las rutas afectadas.
    """
    rutas_afectadas = []  # Lista para almacenar las rutas que se ven afectadas por la congestión
    todas_rutas = []  # Lista para almacenar todas las rutas del grafo
    # Recorre todas las estaciones del grafo
    for estacion in grafo.obtener_estaciones():
        # Para cada estación, obtiene sus rutas vecinas
        for ruta in grafo.obtener_vecinos(estacion):
            todas_rutas.append(ruta)  # Agrega la ruta a la lista de todas_rutas
    # Determina cuántas rutas se van a afectar, asegurándose de afectar al menos una ruta
    n_afectar = max(1, int(len(todas_rutas) * porcentaje))
    # Selecciona aleatoriamente las rutas a afectar
    rutas_seleccionadas = random.sample(todas_rutas, n_afectar)
    # Para cada ruta seleccionada, modifica su peso para simular la congestión
    for ruta in rutas_seleccionadas:
        peso_anterior = ruta.peso  # Almacena el peso anterior de la ruta
        # Selecciona un factor de congestión aleatorio dentro del rango especificado
        factor = random.uniform(factor_min, factor_max)
        # Actualiza el peso de la ruta multiplicándolo por el factor de congestión
        ruta.peso = round(ruta.peso * factor, 2)
        # Agrega la información de la ruta afectada a la lista de rutas_afectadas
        rutas_afectadas.append((ruta.origen.nombre, ruta.dest.nombre, peso_anterior, ruta.peso))
    # Retorna la lista de rutas que fueron afectadas por la simulación de congestión
    return rutas_afectadas

def aplicar_congestion_por_hora(grafo: Grafo, hora: int):
    """
    Ajusta los pesos de las rutas según la hora del día.
    - Hora pico: 6-9 y 17-20 (aumenta pesos 60%)
    - Hora valle: 0-5 y 21-23 (reduce pesos 20%)
    - Resto del día: pesos normales
    """
    for estacion in grafo.obtener_estaciones():
        for ruta in grafo.obtener_vecinos(estacion):
            if 6 <= hora <= 9 or 17 <= hora <= 20:
                ruta.peso = round(ruta.peso * 1.6, 2)
            elif 0 <= hora <= 5 or 21 <= hora <= 23:
                ruta.peso = round(ruta.peso * 0.8, 2)
            # Si es resto del día, no cambia el peso
