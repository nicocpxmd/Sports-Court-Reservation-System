"""
reservation.py
---------------

Define la clase Reservation que vincula un Client y una Court
en una fecha y hora específicas.
"""

from datetime import datetime
from client import Client
from court import Court
import uuid

class Reservation:
    """
    Representa una reserva completa.
    """
    
    def __init__(self, client: Client, court: Court, fecha: str, hora: str, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.client = client
        self.court = court
        self.fecha = fecha
        self.hora = hora
        self.precio = court.precio_por_hora

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.client.nombre,
            "documento": self.client.documento,
            "telefono": self.client.telefono,
            "email": self.client.email,
            "cancha": self.court.tipo,
            "fecha": self.fecha,
            "hora": self.hora,
            "precio": self.precio
        }

    @classmethod
    def from_dict(cls, data: dict):
        client = Client(data["nombre"], data["documento"], data["telefono"], data["email"])
        court = Court(data["cancha"], data.get("precio", 0.0))
        return cls(client, court, data["fecha"], data["hora"], id=data.get("id"))

    def __repr__(self):
        return f"Reservation({self.client.nombre} - {self.court.tipo} - {self.fecha} {self.hora})"