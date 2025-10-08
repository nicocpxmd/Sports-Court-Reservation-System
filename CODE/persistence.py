# Juan David Ocampo Gutierrez
# Nicolás Castro Pacheco
# Michell Valencia Berdugo
# Juan David Rivera Durán


import json
import os
from reservation import Reservation

class Persistence:
    def __init__(self, filepath="reservas.json"):
        # Administra carga/guardado de reservas a un archivo JSON.
        self.filepath = filepath

    def load_reservations(self):
        """Carga reservas desde el JSON. Si no existe, devuelve lista vacía."""
        # Si el archivo no existe, retornamos lista vacía (caso inicial).
        if not os.path.exists(self.filepath):
            return []

        try:
            # Intento de leer y parsear JSON.
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Si el JSON está corrupto o hubo error, tratamos como sin datos.
            data = []

        reservations = []
        for item in data:
            try:
                # Se intenta reconstruir cada reserva; si falla, se ignora y se loggea advertencia.
                reservations.append(Reservation.from_dict(item))
            except Exception as e:
                # Impresión simple a stdout; en producción convendría logging estructurado.
                print(f"[WARN] Reserva inválida ignorada: {e}")
        return reservations

    def save_reservations(self, reservations):
        """Guarda la lista de reservas de forma atómica."""
        # Serializa la lista de Reservation a lista de dicts.
        data = [r.to_dict() for r in reservations]
        temp_path = self.filepath + ".tmp"
        try:
            # Escritura en archivo temporal para evitar corrupción si falla a mitad.
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # Reemplazo atómico (en la mayoría de OS) del archivo original.
            os.replace(temp_path, self.filepath)
        except Exception as e:
            # Si hay error, se limpia el archivo temporal y se reporta.
            print(f"[ERROR] No se pudo guardar reservas: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)