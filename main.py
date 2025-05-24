import json

from src.model.estacion import Estacion
from src.model.grafo import Grafo
from src.model.ruta import Ruta
from src.services.dijkstra import camino_corto
from src.services.ciclos import hay_ciclo
from src.services.conectividad import es_fuertemente_conexo
from src.services.actualizacion import actualizar_peso_ruta
from src.services.sugerencias import sugerir_conexiones

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

# Ejemplo: calcular ruta más corta entre dos estaciones
inicio = grafo.encontrar_estacion("Estacion Central")
fin = grafo.encontrar_estacion("Terminal Sur")
camino, tiempo = camino_corto(grafo, inicio, fin)
print("Ruta más corta de Estacion Central a Terminal Sur:", [e.nombre for e in camino], "Tiempo:", tiempo)

# Ejemplo: detectar ciclos
print("¿Hay ciclos en la red?:", hay_ciclo(grafo))

# Ejemplo: verificar si la red es fuertemente conexa
print("¿La red es fuertemente conexa?:", es_fuertemente_conexo(grafo))

# Ejemplo: actualizar peso de una ruta (simular congestión)
actualizar_peso_ruta(grafo, "Estacion Central", "Plaza Norte", 20)
camino, tiempo = camino_corto(grafo, inicio, fin)
print("Nueva ruta más corta tras congestión:", [e.nombre for e in camino], "Tiempo:", tiempo)

# Ejemplo: sugerir nuevas conexiones con presupuesto de 12 minutos
sugerencias = sugerir_conexiones(grafo, 12)
for origen, destino, tiempo_actual in sugerencias:
    print(f"Sugerencia: conectar {origen.nombre} -> {destino.nombre} (actual: {tiempo_actual} min)")
