import pytest
from src.model.estacion import Estacion
from src.model.grafo import Grafo
from src.model.ruta import Ruta
from src.services.dijkstra import camino_corto
from src.services.ciclos import hay_ciclo
from src.services.conectividad import es_fuertemente_conexo
from src.services.actualizacion import actualizar_peso_ruta
from src.services.sugerencias import sugerir_conexiones

@pytest.fixture
def grafo_simple():
    grafo = Grafo()
    a = Estacion("A")
    b = Estacion("B")
    c = Estacion("C")
    grafo.añadir_estacion(a)
    grafo.añadir_estacion(b)
    grafo.añadir_estacion(c)
    grafo.añadir_ruta(Ruta(a, b, 5))
    grafo.añadir_ruta(Ruta(b, c, 7))
    return grafo

def test_camino_corto(grafo_simple):
    a = grafo_simple.encontrar_estacion("A")
    c = grafo_simple.encontrar_estacion("C")
    camino, tiempo = camino_corto(grafo_simple, a, c)
    assert [e.nombre for e in camino] == ["A", "B", "C"]
    assert tiempo == 12

def test_hay_ciclo(grafo_simple):
    assert not hay_ciclo(grafo_simple)
    a = grafo_simple.encontrar_estacion("A")
    c = grafo_simple.encontrar_estacion("C")
    grafo_simple.añadir_ruta(Ruta(c, a, 2))
    assert hay_ciclo(grafo_simple)

def test_es_fuertemente_conexo(grafo_simple):
    assert not es_fuertemente_conexo(grafo_simple)
    a = grafo_simple.encontrar_estacion("A")
    b = grafo_simple.encontrar_estacion("B")
    c = grafo_simple.encontrar_estacion("C")
    grafo_simple.añadir_ruta(Ruta(c, a, 1))
    grafo_simple.añadir_ruta(Ruta(b, a, 1))
    assert es_fuertemente_conexo(grafo_simple)

def test_actualizar_peso_ruta(grafo_simple):
    a = grafo_simple.encontrar_estacion("A")
    b = grafo_simple.encontrar_estacion("B")
    actualizar_peso_ruta(grafo_simple, "A", "B", 10)
    camino, tiempo = camino_corto(grafo_simple, a, b)
    assert tiempo == 10

def test_sugerir_conexiones(grafo_simple):
    sugerencias = sugerir_conexiones(grafo_simple, 6)
    nombres = [(o.nombre, d.nombre) for o, d, _ in sugerencias]
    assert ("A", "C") in nombres
    assert ("C", "A") in nombres

def test_eliminar_estacion_y_ruta():
    grafo = Grafo()
    a = Estacion("A")
    b = Estacion("B")
    grafo.añadir_estacion(a)
    grafo.añadir_estacion(b)
    grafo.añadir_ruta(Ruta(a, b, 5))
    assert len(grafo.obtener_vecinos(a)) == 1
    grafo.eliminar_ruta(Ruta(a, b, 5))
    assert len(grafo.obtener_vecinos(a)) == 0
    grafo.eliminar_estacion(a)
    assert a not in grafo.obtener_estaciones()

def test_cargar_guardar_grafo(tmp_path):
    grafo = Grafo()
    a = Estacion("A")
    b = Estacion("B")
    grafo.añadir_estacion(a)
    grafo.añadir_estacion(b)
    grafo.añadir_ruta(Ruta(a, b, 5))
    archivo = tmp_path / "grafo.json"
    grafo.guardar_a_json(str(archivo))
    grafo2 = Grafo()
    grafo2.cargar_desde_json(str(archivo))
    assert len(grafo2.obtener_estaciones()) == 2
    assert any(ruta.peso == 5 for ruta in grafo2.obtener_vecinos(grafo2.encontrar_estacion("A")))

def test_simular_congestion():
    grafo = Grafo()
    a = Estacion("A")
    b = Estacion("B")
    grafo.añadir_estacion(a)
    grafo.añadir_estacion(b)
    grafo.añadir_ruta(Ruta(a, b, 10))
    from src.services.actualizacion import simular_congestion
    rutas_afectadas = simular_congestion(grafo, porcentaje=1.0)
    assert len(rutas_afectadas) == 1
    origen, destino, antes, despues = rutas_afectadas[0]
    assert antes == 10
    assert despues != 10

def test_grafo_vacio():
    grafo = Grafo()
    assert grafo.obtener_estaciones() == []
    from src.services.ciclos import hay_ciclo
    from src.services.conectividad import es_fuertemente_conexo
    assert not hay_ciclo(grafo)
    assert es_fuertemente_conexo(grafo)  # Un grafo vacío se considera fuertemente conexo

def test_ruta_inexistente():
    grafo = Grafo()
    a = Estacion("A")
    b = Estacion("B")
    grafo.añadir_estacion(a)
    grafo.añadir_estacion(b)
    from src.services.dijkstra import camino_corto
    camino, tiempo = camino_corto(grafo, a, b)
    assert camino is None or camino == []
    assert tiempo == float("inf")
