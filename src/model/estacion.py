class Estacion:
    """
    Representa una estación o parada en la red de transporte.
    """
    def __init__(self, nombre: str):
        self.nombre = nombre

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return self.nombre

    def __eq__(self, other):
        return isinstance(other, Estacion) and self.nombre == other.nombre

    def __hash__(self):
        return hash(self.nombre)