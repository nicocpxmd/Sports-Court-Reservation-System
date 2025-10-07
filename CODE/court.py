"""
court.py
---------

Define las canchas disponibles y sus precios por hora.
"""

class Court:
    """
    Representa una cancha con su tipo y precio por hora.
    """

    def __init__(self, tipo: str, precio_por_hora: float):
        self.tipo = tipo
        self.precio_por_hora = precio_por_hora

    def to_dict(self):
        return {"tipo": self.tipo, "precio_por_hora": self.precio_por_hora}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["tipo"], data["precio_por_hora"])

    def __repr__(self):
        return f"Court({self.tipo}, ${self.precio_por_hora:.2f}/hora)"