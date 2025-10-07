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
        # id: si no se provee, se genera un UUID4 en formato string.
        self.id = id or str(uuid.uuid4())
        self.client = client
        self.court = court
        self.fecha = fecha
        self.hora = hora
        # Precio se toma directamente del objeto Court en el momento de creación.
        self.precio = court.precio_por_hora

    def to_dict(self):
        # Devuelve un dict "plano" que contiene los campos usados en UI/persistencia.
        # Observación: contiene los datos del cliente duplicados (nombre, documento...) en vez de
        # referenciar un objeto cliente. Esto facilita la persistencia JSON simple.
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
        # Reconstruye Reservation desde el dict guardado.
        # Nota: al crear Client y Court a partir de los campos planos, se validan los datos
        # de cliente mediante las validaciones de Client. Si los datos son inválidos, se lanzará excepción.
        client = Client(data["nombre"], data["documento"], data["telefono"], data["email"])
        # Para Court se toma el tipo y se usa 'precio' si está disponible en el dict.
        court = Court(data["cancha"], data.get("precio", 0.0))
        return cls(client, court, data["fecha"], data["hora"], id=data.get("id"))

    def __repr__(self):
        # Representación útil para logging/depuración.
        return f"Reservation({self.client.nombre} - {self.court.tipo} - {self.fecha} {self.hora})"