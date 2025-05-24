import json

from src.model.estacion import Estacion
from src.model.grafo import Grafo
from src.model.ruta import Ruta

grafo = Grafo()

with open("data/red_ejemplo.json") as archivo:
    datos = json.load(archivo)
    estaciones = [estacion for estacion in (datos["estaciones"])]
    rutas = [ruta for ruta in datos["rutas"]]


for estacion in estaciones:
    estacion_obj = Estacion(estacion)
    grafo.añadir_estacion(estacion_obj)

for ruta in rutas:
    origen = grafo.nombre_a_estacion[ruta["origen"]]
    destino = grafo.nombre_a_estacion[ruta["destino"]]
    peso = ruta["peso"]
    ruta_obj = Ruta(origen,destino,peso)
    grafo.añadir_ruta(ruta_obj)
