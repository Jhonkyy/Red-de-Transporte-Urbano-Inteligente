import json

from src.model.estacion import Estacion
from src.model.grafo import Grafo
from src.model.ruta import Ruta

grafo = Grafo()
grafo.cargar_desde_json("data/red_ejemplo.json")


