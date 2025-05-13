# Taller: Red de Transporte Urbano Inteligente

## Contexto

Una ciudad está implementando un sistema de transporte urbano inteligente que conecte estaciones de metro, paradas de buses y puntos de integración multimodal mediante una red de rutas optimizadas. Esta red se modela como un grafo dirigido y ponderado, donde:

- Los vértices representan estaciones o paradas.
- Las aristas representan rutas disponibles entre ellas.
- Los pesos indican el tiempo promedio de desplazamiento (en minutos) entre dos puntos.

Además, algunas rutas presentan variaciones en sus tiempos por congestión, por lo que los pesos pueden cambiar dinámicamente.

---

## Enunciado del ejercicio

Deben implementar una aplicación en Python que modele la red de transporte como un grafo dirigido y ponderado, e incluya funcionalidades que permitan analizar y optimizar la movilidad en la ciudad.

---

## Actividades a realizar

### 1. Modelar la red como un grafo dirigido y ponderado

- Define clases para vértices (estaciones) y aristas (rutas).
- Permite agregar y eliminar estaciones y rutas.
- Incluye lectura de la red desde un archivo (ej. JSON o texto plano).

### 2. Calcular la ruta más corta entre dos estaciones

- Implementa el algoritmo de Dijkstra.
- Devuelve el camino óptimo y el tiempo total estimado.

### 3. Detectar ciclos en la red

- Usa una estrategia como DFS para identificar ciclos en el grafo.

### 4. Verificar si la red es fuertemente conexa

- Implementa un algoritmo para determinar si se puede llegar desde cualquier estación a cualquier otra.

### 5. Actualizar pesos dinámicamente

- Simula congestión aumentando pesos de ciertas rutas.
- Permite recalcular rutas tras los cambios.

### 6. Sugerir nuevas conexiones

- Dado un presupuesto de tiempo, sugiere nuevas conexiones que reduzcan el tiempo promedio entre estaciones.

### 7. Visualizar la red (opcional)

- Desarrolla una interfaz web que permita visualizar la red de estaciones y rutas.
- Puedes usar librerías como `networkx` (para el análisis) junto con herramientas como **Flask**, **FastAPI**, **NiceGUI** o **Plotly Dash** para construir la interfaz.

---

## Entregables

- Código fuente debidamente documentado.
- Archivo con una red de ejemplo (puede estar en JSON o CSV).
- Capturas o salidas que evidencien el funcionamiento de cada actividad.
- Opcional: interfaz web funcional.

---

## Recomendaciones

- Usa estructuras eficientes como listas de adyacencia y colas de prioridad.
- Organiza el código en clases y funciones reutilizables.
- Aplica pruebas sobre tus algoritmos.
