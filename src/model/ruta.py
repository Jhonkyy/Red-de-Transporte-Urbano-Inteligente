from src.model.estacion import Estacion


class Ruta:
    def __init__(self, origen: Estacion, dest: Estacion, peso: float = 1):
        self.origen = origen
        self.dest = dest
        self.peso = peso

