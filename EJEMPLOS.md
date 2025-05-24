# Ejemplos de uso y salidas

## Ruta más corta entre dos estaciones

```python
from src.services.dijkstra import camino_corto

inicio = grafo.encontrar_estacion("Estacion Central")
fin = grafo.encontrar_estacion("Terminal Sur")
camino, tiempo = camino_corto(grafo, inicio, fin)
print("Ruta más corta de Estacion Central a Terminal Sur:", [e.nombre for e in camino], "Tiempo:", tiempo)
```
Salida esperada:
```
Ruta más corta de Estacion Central a Terminal Sur: ['Estacion Central', 'Plaza Norte', 'Terminal Sur'] Tiempo: 18
```

## Detección de ciclos

```python
from src.services.ciclos import hay_ciclo
print("¿Hay ciclos en la red?:", hay_ciclo(grafo))
```
Salida esperada:
```
¿Hay ciclos en la red?: False
```

## Verificar si la red es fuertemente conexa

```python
from src.services.conectividad import es_fuertemente_conexo
print("¿La red es fuertemente conexa?:", es_fuertemente_conexo(grafo))
```
Salida esperada:
```
¿La red es fuertemente conexa?: False
```

## Actualizar peso de una ruta (simular congestión)

```python
from src.services.actualizacion import actualizar_peso_ruta
actualizar_peso_ruta(grafo, "Estacion Central", "Plaza Norte", 20)
camino, tiempo = camino_corto(grafo, inicio, fin)
print("Nueva ruta más corta tras congestión:", [e.nombre for e in camino], "Tiempo:", tiempo)
```
Salida esperada:
```
Nueva ruta más corta tras congestión: ['Estacion Central', 'Plaza Norte', 'Terminal Sur'] Tiempo: 30
```

## Sugerir nuevas conexiones

```python
from src.services.sugerencias import sugerir_conexiones
sugerencias = sugerir_conexiones(grafo, 12)
for origen, destino, tiempo_actual in sugerencias:
    print(f"Sugerencia: conectar {origen.nombre} -> {destino.nombre} (actual: {tiempo_actual} min)")
```
Salida esperada:
```
Sugerencia: conectar Plaza Norte -> Estacion Central (actual: inf min)
Sugerencia: conectar Estacion Central -> Terminal Sur (actual: 30 min)
Sugerencia: conectar Terminal Sur -> Estacion Central (actual: inf min)
Sugerencia: conectar Terminal Sur -> Plaza Norte (actual: inf min)
```
