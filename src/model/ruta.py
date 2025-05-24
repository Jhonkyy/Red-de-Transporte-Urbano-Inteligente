from src.model.estacion import Estacion


class Ruta:
    """
    Representa una ruta dirigida y ponderada entre dos estaciones.
    """

    def __init__(self, origen: Estacion, dest: Estacion, peso: float = 1):
        self.origen = origen
        self.dest = dest
        self.peso = peso

    def __eq__(self, other):
        if not isinstance(other, Ruta):
            return False
        return (
            self.origen == other.origen
            and self.dest == other.dest
            and self.peso == other.peso
        )

    def __hash__(self):
        return hash((self.origen, self.dest, self.peso))

