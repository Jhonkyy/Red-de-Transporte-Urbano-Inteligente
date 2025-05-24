from flask import Flask, Response, render_template_string, request
import io
import matplotlib.pyplot as plt
import networkx as nx
import json
from src.model.grafo import Grafo
from src.model.estacion import Estacion
from src.model.ruta import Ruta
from src.services.dijkstra import camino_corto
from src.services.actualizacion import simular_congestion
import heapq

app = Flask(__name__)

# --- GRAFO GLOBAL PARA MANTENER EL ESTADO ENTRE PETICIONES ---
grafo_global = None

def cargar_grafo():
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
        ruta_obj = Ruta(origen, destino, peso)
        grafo.añadir_ruta(ruta_obj)
    return grafo

def get_grafo():
    global grafo_global
    if grafo_global is None:
        grafo_global = cargar_grafo()
    return grafo_global

def reset_grafo():
    global grafo_global
    grafo_global = cargar_grafo()

def grafo_a_networkx(grafo: Grafo):
    G = nx.DiGraph()
    for estacion in grafo.obtener_estaciones():
        G.add_node(estacion.nombre)
    for estacion in grafo.obtener_estaciones():
        for ruta in grafo.obtener_vecinos(estacion):
            G.add_edge(ruta.origen.nombre, ruta.dest.nombre, weight=ruta.peso)
    return G

@app.route("/", methods=["GET", "POST"])
def index():
    grafo = get_grafo()
    estaciones = [e.nombre for e in grafo.obtener_estaciones()]
    rutas = []
    for estacion in grafo.obtener_estaciones():
        for ruta in grafo.obtener_vecinos(estacion):
            rutas.append({
                "origen": ruta.origen.nombre,
                "destino": ruta.dest.nombre,
                "peso": ruta.peso
            })

    camino = []
    tiempo = None
    origen_sel = None
    destino_sel = None
    rutas_afectadas = None

    if request.method == "POST":
        if "simular_congestion" in request.form:
            rutas_afectadas = simular_congestion(grafo, porcentaje=0.5)
        elif "reset" in request.form:
            reset_grafo()
            grafo = get_grafo()
        else:
            origen_sel = request.form.get("origen")
            destino_sel = request.form.get("destino")
            if origen_sel and destino_sel and origen_sel != destino_sel:
                origen_obj = grafo.encontrar_estacion(origen_sel)
                destino_obj = grafo.encontrar_estacion(destino_sel)
                camino, tiempo = camino_corto(grafo, origen_obj, destino_obj)
                if camino is None:
                    camino = []
                    tiempo = None

    html = """
    <html>
    <head>
        <title>Red de Transporte Urbano</title>
        <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Montserrat', Arial, sans-serif;
                background: linear-gradient(120deg, #e0eafc, #cfdef3);
                margin: 0;
                padding: 0;
            }
            header {
                background: #2980b9;
                color: #fff;
                padding: 20px 0;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px #bbb;
            }
            .container {
                max-width: 1000px;
                margin: 30px auto;
                background: #fff;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 0 20px #b0c4de;
            }
            h1, h2 {
                color: #2c3e50;
            }
            nav {
                margin-bottom: 20px;
                text-align: right;
            }
            nav a {
                margin-left: 20px;
                color: #2980b9;
                text-decoration: none;
                font-weight: bold;
                transition: color 0.2s;
            }
            nav a:hover {
                color: #1abc9c;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                border-radius: 8px;
                overflow: hidden;
            }
            th, td {
                border: 1px solid #bbb;
                padding: 10px;
                text-align: center;
            }
            th {
                background: #2980b9;
                color: #fff;
            }
            tr:nth-child(even) {
                background: #f2f2f2;
            }
            .img-container {
                text-align: center;
                margin-bottom: 20px;
            }
            .form-section {
                margin-bottom: 30px;
                text-align: center;
            }
            .form-section select, .form-section button {
                padding: 8px 12px;
                margin: 0 8px;
                border-radius: 6px;
                border: 1px solid #2980b9;
                font-size: 1em;
            }
            .form-section button {
                background: #2980b9;
                color: #fff;
                border: none;
                cursor: pointer;
                transition: background 0.2s;
            }
            .form-section button:hover {
                background: #1abc9c;
            }
            .shortest-path {
                background: #eaf6ff;
                padding: 14px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 1.1em;
                text-align: center;
                border-left: 5px solid #2980b9;
            }
            ul {
                columns: 2;
                -webkit-columns: 2;
                -moz-columns: 2;
                margin-bottom: 30px;
            }
            @media (max-width: 700px) {
                .container { padding: 10px; }
                ul { columns: 1; }
            }
        </style>
    </head>
    <body>
        <header>
            <h1>🚇 Red de Transporte Urbano Inteligente</h1>
        </header>
        <div class="container">
            <nav>
                <a href="/">Inicio</a>
                <a href="/ayuda">Ayuda</a>
            </nav>
            <h1>Visualización de la Red de Transporte Urbano</h1>
            <div class="form-section">
                <form method="post" style="display:inline;">
                    <label for="origen">Estación origen:</label>
                    <select name="origen" id="origen" required>
                        <option value="">Seleccione</option>
                        {% for estacion in estaciones %}
                            <option value="{{ estacion }}" {% if estacion == origen_sel %}selected{% endif %}>{{ estacion }}</option>
                        {% endfor %}
                    </select>
                    <label for="destino">Estación destino:</label>
                    <select name="destino" id="destino" required>
                        <option value="">Seleccione</option>
                        {% for estacion in estaciones %}
                            <option value="{{ estacion }}" {% if estacion == destino_sel %}selected{% endif %}>{{ estacion }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit">Mostrar camino más corto</button>
                </form>
                <form method="post" style="display:inline;">
                    <button type="submit" name="simular_congestion" value="1" style="background:#e67e22; color:#fff; margin-left:20px;">Simular congestión</button>
                </form>
                <form method="post" style="display:inline;">
                    <button type="submit" name="reset" value="1" style="background:#c0392b; color:#fff; margin-left:20px;">Restablecer red</button>
                </form>
            </div>
            {% if rutas_afectadas %}
                <div class="shortest-path" style="background:#fffbe6; border-left:5px solid #e67e22;">
                    <b>Rutas afectadas por congestión:</b>
                    <ul>
                    {% for origen, destino, antes, despues in rutas_afectadas %}
                        <li>Ruta {{ origen }} → {{ destino }}: {{ antes }} min → <b>{{ despues }} min</b></li>
                    {% endfor %}
                    </ul>
                </div>
            {% endif %}
            {% if camino and tiempo is not none %}
                <div class="shortest-path">
                    <b>Camino más corto:</b>
                    {{ camino|join(" → ") }}<br>
                    <b>Tiempo total:</b> {{ tiempo }} minutos
                </div>
            {% elif origen_sel and destino_sel %}
                <div class="shortest-path">
                    <b>No hay camino entre las estaciones seleccionadas.</b>
                </div>
            {% endif %}
            <div class="img-container">
                <img src="/grafo.png?origen={{ origen_sel }}&destino={{ destino_sel }}" alt="Grafo de la red">
            </div>
            <h2>Estaciones</h2>
            <ul>
                {% for estacion in estaciones %}
                    <li>{{ estacion }}</li>
                {% endfor %}
            </ul>
            <h2>Rutas</h2>
            <table>
                <tr>
                    <th>Origen</th>
                    <th>Destino</th>
                    <th>Peso (minutos)</th>
                </tr>
                {% for ruta in rutas %}
                <tr>
                    <td>{{ ruta.origen }}</td>
                    <td>{{ ruta.destino }}</td>
                    <td>{{ ruta.peso }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    camino_nombres = [e.nombre for e in camino] if camino else []
    return render_template_string(
        html,
        estaciones=estaciones,
        rutas=rutas,
        camino=camino_nombres,
        tiempo=tiempo,
        origen_sel=origen_sel,
        destino_sel=destino_sel,
        rutas_afectadas=rutas_afectadas
    )

@app.route("/ayuda")
def ayuda():
    html = """
    <html>
    <head>
        <title>Ayuda - Red de Transporte Urbano</title>
        <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Montserrat', Arial, sans-serif;
                background: linear-gradient(120deg, #e0eafc, #cfdef3);
                margin: 0;
                padding: 0;
            }
            header {
                background: #2980b9;
                color: #fff;
                padding: 20px 0;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px #bbb;
            }
            .container {
                max-width: 800px;
                margin: 30px auto;
                background: #fff;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 0 20px #b0c4de;
            }
            h1, h2 {
                color: #2c3e50;
            }
            ul {
                margin-bottom: 20px;
            }
            .legend {
                margin: 20px 0;
                padding: 16px;
                background: #eaf6ff;
                border-radius: 8px;
                border-left: 5px solid #2980b9;
            }
            a {
                color: #2980b9;
                text-decoration: none;
                font-weight: bold;
                transition: color 0.2s;
            }
            a:hover {
                color: #1abc9c;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Ayuda</h1>
        </header>
        <div class="container">
            <h2>¿Cómo usar la Red de Transporte Urbano?</h2>
            <ul>
                <li>Selecciona una estación de origen y una de destino en el formulario principal.</li>
                <li>Haz clic en <b>Mostrar camino más corto</b> para ver la ruta óptima y el tiempo total.</li>
                <li>La red se visualiza with colores para facilitar la interpretación de los tiempos de viaje.</li>
            </ul>
            <div class="legend">
                <b>Colores de las aristas:</b>
                <ul>
                    <li style="color:green;">Verde: rutas rápidas (≤ 7 min)</li>
                    <li style="color:orange;">Naranja: rutas medias (8-12 min)</li>
                    <li style="color:red;">Rojo: rutas lentas (&gt; 12 min)</li>
                    <li style="color:blue;">Azul: camino más corto seleccionado</li>
                </ul>
            </div>
            <a href="/">← Volver al inicio</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/grafo.png")
def mostrar_grafo():
    grafo = cargar_grafo()
    G = grafo_a_networkx(grafo)

    # Posiciones fijas para las estaciones
    pos = {
        "Estacion Central": (0, 0),
        "Plaza Norte": (0.2, 1.5),
        "Terminal Sur": (1, -0.6),
        "Estacion Este": (1.5, 2),
        "Estacion Oeste": (0.3, -2),
        "Intercambiador": (3.2, -2),
        "Parque Central": (3, 0),
        "Universidad": (4, 2),
        "Hospital": (4, 0),
        "Aeropuerto": (5, 1)
    }

    # Obtener parámetros de la URL para resaltar el camino más corto
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    shortest_edges = []
    if origen and destino and origen != destino and origen in G.nodes and destino in G.nodes:
        # Reconstruir el grafo y buscar el camino más corto
        grafo_obj = cargar_grafo()
        origen_obj = grafo_obj.encontrar_estacion(origen)
        destino_obj = grafo_obj.encontrar_estacion(destino)
        camino, _ = camino_corto(grafo_obj, origen_obj, destino_obj)
        if camino and len(camino) > 1:
            camino_nombres = [e.nombre for e in camino]
            shortest_edges = [(camino_nombres[i], camino_nombres[i+1]) for i in range(len(camino_nombres)-1)]

    plt.figure(figsize=(12, 9))

    # Obtener pesos y asignar colores
    edges = G.edges(data=True)
    edge_colors = []
    for u, v, data in edges:
        if (u, v) in shortest_edges:
            edge_colors.append('blue')
        else:
            peso = data['weight']
            if peso <= 7:
                edge_colors.append('green')
            elif peso <= 12:
                edge_colors.append('orange')
            else:
                edge_colors.append('red')

    nx.draw(
        G, pos, with_labels=True, node_color='lightblue', node_size=2000,
        font_size=10, arrowsize=20, edge_color=edge_colors, width=2
    )
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return Response(buf.getvalue(), mimetype='image/png')

def camino_corto(grafo, inicio, destino):
    distances = {node: float("inf") for node in grafo.obtener_estaciones()}
    anterior = {node: None for node in grafo.obtener_estaciones()}
    distances[inicio] = 0
    visitados = set()
    heap = [(0, inicio.nombre, inicio)]  # Agrega el nombre como segundo elemento

    while heap:
        distancia_actual, _, current = heapq.heappop(heap)
        if current in visitados:
            continue
        visitados.add(current)
        if current == destino:
            break
        for vecino in grafo.obtener_vecinos(current):
            peso = vecino.peso
            nodo_vecino = vecino.dest
            tentativa = distances[current] + peso
            if tentativa < distances[nodo_vecino]:
                distances[nodo_vecino] = tentativa
                anterior[nodo_vecino] = current
                heapq.heappush(heap, (tentativa, nodo_vecino.nombre, nodo_vecino))

    # Reconstruir el camino óptimo
    camino = []
    actual = destino
    while actual is not None:
        camino.insert(0, actual)
        actual = anterior[actual]
    if distances[destino] == float("inf"):
        return None, float("inf")  # No hay camino
    return camino, distances[destino]

if __name__ == "__main__":
    app.run(debug=True)
