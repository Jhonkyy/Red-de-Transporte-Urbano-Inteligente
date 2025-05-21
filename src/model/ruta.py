from src.model.estacion import Estacion


class Ruta:
    def __init__(self, origen: Estacion, dest: Estacion, peso: float):
        self.origen = origen
        self.dest = dest
        self.peso = peso

