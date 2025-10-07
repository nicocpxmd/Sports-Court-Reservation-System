from datetime import datetime, date
from typing import List, Dict, Optional
from client import Client
from court import Court
from reservation import Reservation
from persistence import Persistence

class Manager:
    def __init__(self):
        self.persistence = Persistence("reservas.json")
        self.courts = self._load_courts()
        self.reservations: List[Reservation] = self.persistence.load_reservations()

    # ------------------------------
    # Carga inicial de canchas
    # ------------------------------
    def _load_courts(self):
        return [Court("Sintética", 5.0), Court("Vóley", 7.5)]

    def get_court_types(self):
        return [c.tipo for c in self.courts]

    def get_price_for_court(self, tipo: str) -> float:
        c = next((x for x in self.courts if x.tipo == tipo), None)
        return c.precio_por_hora if c else 0.0

    # ------------------------------
    # Validaciones internas
    # ------------------------------
    def __hour_to_int(self, hora: str) -> int:
        try:
            return int(hora.split(":")[0])
        except Exception:
            raise ValueError("Formato de hora inválido. Debe ser 'HH:00'")

    def __validate_hour_in_range(self, hora: str):
        h = self.__hour_to_int(hora)
        if h < 10 or h > 21:
            raise ValueError("Hora fuera de rango. Rango permitido: 10:00 - 21:00")

    def __validate_fecha_not_past(self, fecha: str):
        try:
            d = datetime.strptime(fecha, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
        if d < date.today():
            raise ValueError("No se pueden crear reservas en fechas pasadas.")

    # ------------------------------
    # Disponibilidad
    # ------------------------------
    def check_availability(self, cancha: str, fecha: str, hora: str, exclude_id: Optional[str] = None) -> bool:
        """True si la cancha está disponible en fecha/hora, ignorando exclude_id (para edición)."""
        for r in self.reservations:
            if exclude_id and r.id == exclude_id:
                continue
            if r.court.tipo == cancha and r.fecha == fecha and r.hora == hora:
                return False
        return True

    # ------------------------------
    # Crear reserva
    # ------------------------------
    def create_reservation(self, nombre: str, documento: str, telefono: str,
                           email: str, cancha: str, fecha: str, hora: str) -> None:
        self.__validate_fecha_not_past(fecha)
        self.__validate_hour_in_range(hora)

        client = Client(nombre, documento, telefono, email)
        court = next((c for c in self.courts if c.tipo == cancha), None)
        if not court:
            raise ValueError("Cancha no válida.")

        if not self.check_availability(cancha, fecha, hora):
            raise ValueError("Esa hora ya está ocupada para la cancha seleccionada.")

        r = Reservation(client, court, fecha, hora)
        self.reservations.append(r)
        self.persistence.save_reservations(self.reservations)

    # ------------------------------
    # Listar reservas
    # ------------------------------
    def get_all_reservations(self) -> List[Dict]:
        return [r.to_dict() for r in self.reservations]

    # ------------------------------
    # Buscar por ID
    # ------------------------------
    def get_reservation_by_id(self, res_id: str) -> Optional[Reservation]:
        return next((r for r in self.reservations if r.id == res_id), None)

    def get_reservation_index_by_id(self, res_id: str) -> int:
        for i, r in enumerate(self.reservations):
            if r.id == res_id:
                return i
        return -1

    # ------------------------------
    # Editar reserva
    # ------------------------------
    def edit_reservation_by_id(self, res_id: str, **kwargs) -> None:
        """Edita una reserva existente por su ID único."""
        r = self.get_reservation_by_id(res_id)
        if not r:
            raise ValueError("Reserva no encontrada.")

        # Nuevos valores (mantiene los antiguos si no se pasan)
        nombre = kwargs.get("nombre", r.client.nombre)
        documento = kwargs.get("documento", r.client.documento)
        telefono = kwargs.get("telefono", r.client.telefono)
        email = kwargs.get("email", r.client.email)
        cancha = kwargs.get("cancha", r.court.tipo)
        fecha = kwargs.get("fecha", r.fecha)
        hora = kwargs.get("hora", r.hora)

        self.__validate_fecha_not_past(fecha)
        self.__validate_hour_in_range(hora)

        court_obj = next((c for c in self.courts if c.tipo == cancha), None)
        if not court_obj:
            raise ValueError("Cancha no válida.")

        if not self.check_availability(cancha, fecha, hora, exclude_id=res_id):
            raise ValueError("La nueva fecha/hora está ocupada para la cancha seleccionada.")

        new_client = Client(nombre, documento, telefono, email)

        # Actualizar campos
        r.client = new_client
        r.court = court_obj
        r.fecha = fecha
        r.hora = hora
        r.precio = court_obj.precio_por_hora

        self.persistence.save_reservations(self.reservations)

    # ------------------------------
    # Cancelar reserva
    # ------------------------------
    def cancel_reservation_by_id(self, res_id: str) -> None:
        idx = self.get_reservation_index_by_id(res_id)
        if idx == -1:
            raise ValueError("Reserva no encontrada.")
        del self.reservations[idx]
        self.persistence.save_reservations(self.reservations)

    # ------------------------------
    # Guardar manualmente
    # ------------------------------
    def save_all(self) -> None:
        self.persistence.save_reservations(self.reservations)