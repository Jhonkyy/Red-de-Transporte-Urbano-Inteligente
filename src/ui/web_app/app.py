from flask import Flask, Response, render_template_string, request
import io
import matplotlib.pyplot as plt
import networkx as nx
import json
from src.model.grafo import Grafo
from src.model.estacion import Estacion
from src.model.ruta import Ruta
from src.services.dijkstra import camino_corto
from src.services.actualizacion import simular_congestion, aplicar_congestion_por_hora
from src.services.sugerencias import sugerir_conexiones
import heapq

def k_caminos_mas_rapidos(grafo, origen, destino, k=3):
    """
    Devuelve hasta k caminos más cortos (por tiempo) entre origen y destino usando una variante de Yen's algorithm.
    Cada camino es una lista de estaciones.
    """
    import copy
    from collections import deque

    def dijkstra_path(grafo, inicio, fin):
        distances = {node: float("inf") for node in grafo.obtener_estaciones()}
        anterior = {node: None for node in grafo.obtener_estaciones()}
        distances[inicio] = 0
        heap = [(0, inicio)]
        while heap:
            distancia_actual, current = heapq.heappop(heap)
            if current == fin:
                break
            for vecino in grafo.obtener_vecinos(current):
                peso = vecino.peso
                nodo_vecino = vecino.dest
                tentativa = distances[current] + peso
                if tentativa < distances[nodo_vecino]:
                    distances[nodo_vecino] = tentativa
                    anterior[nodo_vecino] = current
                    heapq.heappush(heap, (tentativa, nodo_vecino))
        # reconstruir camino
        camino = []
        actual = fin
        while actual is not None:
            camino.insert(0, actual)
            actual = anterior[actual]
        if distances[fin] == float("inf"):
            return None, float("inf")
        return camino, distances[fin]

    caminos = []
    costos = []
    primer_camino, primer_costo = dijkstra_path(grafo, origen, destino)
    if not primer_camino or len(primer_camino) < 2:
        return []
    caminos.append(primer_camino)
    costos.append(primer_costo)
    candidatos = []
    for k_actual in range(1, k):
        for i in range(len(caminos[-1]) - 1):
            grafo_temp = copy.deepcopy(grafo)
            spur_node = caminos[-1][i]
            root_path = caminos[-1][:i+1]
            # Elimina aristas que ya están en los caminos previos con el mismo root_path
            for camino_prev in caminos:
                if len(camino_prev) > i and camino_prev[:i+1] == root_path:
                    u = camino_prev[i]
                    v = camino_prev[i+1]
                    rutas_a_eliminar = [ruta for ruta in grafo_temp.obtener_vecinos(u) if ruta.dest == v]
                    for ruta in rutas_a_eliminar:
                        grafo_temp.eliminar_ruta(ruta)
            # Elimina nodos del root_path excepto spur_node
            for nodo in root_path[:-1]:
                grafo_temp.eliminar_estacion(nodo)
            spur_path, spur_cost = dijkstra_path(grafo_temp, spur_node, destino)
            if spur_path and len(spur_path) > 1:
                total_path = root_path[:-1] + spur_path
                if total_path not in caminos and all([total_path != c for c, _ in candidatos]):
                    total_cost = 0
                    for j in range(len(total_path)-1):
                        for ruta in grafo.obtener_vecinos(total_path[j]):
                            if ruta.dest == total_path[j+1]:
                                total_cost += ruta.peso
                                break
                    candidatos.append((total_path, total_cost))
        if not candidatos:
            break
        candidatos.sort(key=lambda x: x[1])
        caminos.append(candidatos[0][0])
        costos.append(candidatos[0][1])
        candidatos.pop(0)
    return list(zip(caminos, costos))

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
    hora_sel = None
    mensaje_hora = None
    caminos_k = []
    k_sel = 1
    sugerencias = []
    presupuesto_sel = 12

    if request.method == "POST":
        if "simular_congestion" in request.form:
            rutas_afectadas = simular_congestion(grafo, porcentaje=0.5)
        elif "reset" in request.form:
            reset_grafo()
            grafo = get_grafo()
        elif "aplicar_hora" in request.form:
            hora_sel = int(request.form.get("hora", 8))
            aplicar_congestion_por_hora(grafo, hora_sel)
            mensaje_hora = f"<b>Congestión aplicada para la hora seleccionada:</b> <span style='color:#16a085'>{hora_sel:02d}:00</span>"
        elif "mostrar_k_caminos" in request.form:
            origen_sel = request.form.get("origen")
            destino_sel = request.form.get("destino")
            k_sel = int(request.form.get("k", 1))
            if origen_sel and destino_sel and origen_sel != destino_sel:
                origen_obj = grafo.encontrar_estacion(origen_sel)
                destino_obj = grafo.encontrar_estacion(destino_sel)
                caminos_k = k_caminos_mas_rapidos(grafo, origen_obj, destino_obj, k=k_sel)
        elif "sugerir_conexiones" in request.form:
            presupuesto_sel = int(request.form.get("presupuesto", 12))
            sugerencias = sugerir_conexiones(grafo, presupuesto_sel)
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
                    <input type="hidden" name="origen" value="{{ origen_sel or '' }}">
                    <input type="hidden" name="destino" value="{{ destino_sel or '' }}">
                    <label for="k">Ver los</label>
                    <select name="k" id="k">
                        {% for i in range(1,4) %}
                            <option value="{{ i }}" {% if k_sel == i %}selected{% endif %}>{{ i }}</option>
                        {% endfor %}
                    </select>
                    <label>caminos más rápidos</label>
                    <button type="submit" name="mostrar_k_caminos" value="1" style="background:#8e44ad; color:#fff; margin-left:10px;">Mostrar</button>
                </form>
                <form method="post" style="display:inline;">
                    <button type="submit" name="simular_congestion" value="1" style="background:#e67e22; color:#fff; margin-left:20px;">Simular congestión</button>
                </form>
                <form method="post" style="display:inline;">
                    <button type="submit" name="reset" value="1" style="background:#c0392b; color:#fff; margin-left:20px;">Restablecer red</button>
                </form>
                <form method="post" style="display:inline;">
                    <label for="hora">Simular hora del día:</label>
                    <select name="hora" id="hora">
                        {% for h in range(0,24) %}
                            <option value="{{ h }}" {% if hora_sel is not none and h == hora_sel %}selected{% endif %}>{{ "%02d:00" % h }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit" name="aplicar_hora" value="1" style="background:#16a085; color:#fff; margin-left:10px;">Aplicar congestión por hora</button>
                </form>
                <form method="post" style="display:inline;">
                    <label for="presupuesto">Sugerir nuevas conexiones (presupuesto en minutos):</label>
                    <select name="presupuesto" id="presupuesto">
                        {% for p in range(6, 31, 2) %}
                            <option value="{{ p }}" {% if presupuesto_sel == p %}selected{% endif %}>{{ p }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit" name="sugerir_conexiones" value="1" style="background:#2980b9; color:#fff; margin-left:10px;">Sugerir conexiones</button>
                </form>
            </div>
            {% if mensaje_hora %}
                <div class="shortest-path" style="background:#e0f7fa; border-left:5px solid #16a085;">
                    {{ mensaje_hora|safe }}
                </div>
            {% endif %}
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
            {% if sugerencias %}
                <div class="shortest-path" style="background:#eaf6ff; border-left:5px solid #2980b9;">
                    <b>Sugerencias de nuevas conexiones:</b>
                    <ul>
                    {% for origen, destino, tiempo_actual in sugerencias %}
                        <li>Conectar <b>{{ origen.nombre }}</b> → <b>{{ destino.nombre }}</b> (actual: {{ tiempo_actual }} min)</li>
                    {% endfor %}
                    </ul>
                </div>
            {% endif %}
            {% if caminos_k %}
                <div class="shortest-path" style="background:#f3e6ff; border-left:5px solid #8e44ad;">
                    <b>Caminos más rápidos:</b>
                    <ol>
                    {% for camino, costo in caminos_k %}
                        <li>{{ camino|map(attribute='nombre')|join(" → ") }} <span style="color:#888;">({{ costo }} min)</span></li>
                    {% endfor %}
                    </ol>
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
        rutas_afectadas=rutas_afectadas,
        hora_sel=hora_sel,
        mensaje_hora=mensaje_hora,
        caminos_k=caminos_k,
        k_sel=k_sel,
        sugerencias=sugerencias,
        presupuesto_sel=presupuesto_sel
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
    grafo = get_grafo()  # Usar el grafo global, no cargar_grafo()
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
        # Usar el grafo global para buscar el camino más corto
        origen_obj = grafo.encontrar_estacion(origen)
        destino_obj = grafo.encontrar_estacion(destino)
        camino, _ = camino_corto(grafo, origen_obj, destino_obj)
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
