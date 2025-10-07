import json
import os
from reservation import Reservation

class Persistence:
    def __init__(self, filepath="reservas.json"):
        self.filepath = filepath

    def load_reservations(self):
        """Carga reservas desde el JSON. Si no existe, devuelve lista vacía."""
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []

        reservations = []
        for item in data:
            try:
                reservations.append(Reservation.from_dict(item))
            except Exception as e:
                print(f"[WARN] Reserva inválida ignorada: {e}")
        return reservations

    def save_reservations(self, reservations):
        """Guarda la lista de reservas de forma atómica."""
        data = [r.to_dict() for r in reservations]
        temp_path = self.filepath + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception as e:
            print(f"[ERROR] No se pudo guardar reservas: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
