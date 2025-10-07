"""
court.py
---------

Define las canchas disponibles y sus precios por hora.
"""

class Court:
    """
    Representa una cancha con su tipo y precio por hora.
    """
    # ------------------------------------------------------------
    # Explicación:
    # - Clase ligera/valor que contiene 'tipo' (nombre) y 'precio_por_hora'.
    # - Usada por Manager y Reservation para determinar precio y tipo.
    # - Incluye to_dict / from_dict para interoperabilidad con persistencia.
    # ------------------------------------------------------------

    def __init__(self, tipo: str, precio_por_hora: float):
        self.tipo = tipo
        self.precio_por_hora = precio_por_hora

    def to_dict(self):
        # Serializa la cancha a dict.
        return {"tipo": self.tipo, "precio_por_hora": self.precio_por_hora}

    @classmethod
    def from_dict(cls, data: dict):
        # Reconstruye Court desde dict.
        return cls(data["tipo"], data["precio_por_hora"])

    def __repr__(self):
        # Representación amigable con formato de precio.
        return f"Court({self.tipo}, ${self.precio_por_hora:.2f}/hora)"