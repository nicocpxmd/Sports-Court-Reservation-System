# Juan David Ocampo Gutierrez
# Nicolás Castro Pacheco
# Michell Valencia Berdugo
# Juan David Rivera Durán


from datetime import datetime, date
from typing import List, Dict, Optional
from client import Client
from court import Court
from reservation import Reservation
from persistence import Persistence

class Manager:
    def __init__(self):
        # Persistence maneja el archivo JSON de reservas.
        self.persistence = Persistence("reservas.json")
        # Inicializa las canchas disponibles (puede extenderse fácilmente).
        self.courts = self._load_courts()
        # Carga las reservas persistidas (lista de objetos Reservation).
        self.reservations: List[Reservation] = self.persistence.load_reservations()

    # ------------------------------
    # Carga inicial de canchas
    # ------------------------------
    def _load_courts(self):
        # Devuelve lista de Court predefinidas.
        return [Court("Sintética", 5.0), Court("Vóley", 7.5)]

    def get_court_types(self):
        # Útil para poblar UIs: lista de nombres de canchas.
        return [c.tipo for c in self.courts]

    def get_price_for_court(self, tipo: str) -> float:
        # Busca la cancha por tipo y retorna su precio, o 0.0 si no existe.
        c = next((x for x in self.courts if x.tipo == tipo), None)
        return c.precio_por_hora if c else 0.0

    # ------------------------------
    # Validaciones internas
    # ------------------------------
    def __hour_to_int(self, hora: str) -> int:
        # Convierte "HH:MM" a entero con la hora (HH). Lanza ValueError en formato inválido.
        try:
            return int(hora.split(":")[0])
        except Exception:
            raise ValueError("Formato de hora inválido. Debe ser 'HH:00'")

    def __validate_hour_in_range(self, hora: str):
        # Se permite rango 10 a 21 (inclusive). Lanza ValueError si está fuera del rango.
        h = self.__hour_to_int(hora)
        if h < 10 or h > 21:
            raise ValueError("Hora fuera de rango. Rango permitido: 10:00 - 21:00")

    def __validate_fecha_not_past(self, fecha: str):
        # Valida formato YYYY-MM-DD y que la fecha no sea pasada.
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
        # Recorre las reservas cargadas y verifica colisión por cancha+fecha+hora.
        for r in self.reservations:
            if exclude_id and r.id == exclude_id:
                # Permite ignorar la propia reserva al editar.
                continue
            if r.court.tipo == cancha and r.fecha == fecha and r.hora == hora:
                return False
        return True

    # ------------------------------
    # Crear reserva
    # ------------------------------
    def create_reservation(self, nombre: str, documento: str, telefono: str,
                           email: str, cancha: str, fecha: str, hora: str) -> None:
        # Valida fecha y hora antes de instanciar objetos que validan sus campos.
        self.__validate_fecha_not_past(fecha)
        self.__validate_hour_in_range(hora)

        # Crear objetos Client y Court; Client valida campos personales.
        client = Client(nombre, documento, telefono, email)
        court = next((c for c in self.courts if c.tipo == cancha), None)
        if not court:
            raise ValueError("Cancha no válida.")

        # Verificar disponibilidad
        if not self.check_availability(cancha, fecha, hora):
            raise ValueError("Esa hora ya está ocupada para la cancha seleccionada.")

        # Crear Reservation y persistir
        r = Reservation(client, court, fecha, hora)
        self.reservations.append(r)
        self.persistence.save_reservations(self.reservations)

    # ------------------------------
    # Listar reservas
    # ------------------------------
    def get_all_reservations(self) -> List[Dict]:
        # Devuelve una lista de dicts (usado por la UI para mostrar datos).
        return [r.to_dict() for r in self.reservations]

    # ------------------------------
    # Buscar por ID
    # ------------------------------
    def get_reservation_by_id(self, res_id: str) -> Optional[Reservation]:
        # Retorna el objeto Reservation o None.
        return next((r for r in self.reservations if r.id == res_id), None)

    def get_reservation_index_by_id(self, res_id: str) -> int:
        # Retorna índice en la lista o -1 si no existe (útil para eliminar).
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

        # Validaciones
        self.__validate_fecha_not_past(fecha)
        self.__validate_hour_in_range(hora)

        # Verificar que la cancha exista
        court_obj = next((c for c in self.courts if c.tipo == cancha), None)
        if not court_obj:
            raise ValueError("Cancha no válida.")

        # Comprobar disponibilidad ignorando la reserva actual (exclude_id)
        if not self.check_availability(cancha, fecha, hora, exclude_id=res_id):
            raise ValueError("La nueva fecha/hora está ocupada para la cancha seleccionada.")

        # Crear un nuevo Client (revalida datos del cliente)
        new_client = Client(nombre, documento, telefono, email)

        # Actualizar campos de la reserva existente
        r.client = new_client
        r.court = court_obj
        r.fecha = fecha
        r.hora = hora
        r.precio = court_obj.precio_por_hora

        # Persistir cambios
        self.persistence.save_reservations(self.reservations)

    # ------------------------------
    # Cancelar reserva
    # ------------------------------
    def cancel_reservation_by_id(self, res_id: str) -> None:
        idx = self.get_reservation_index_by_id(res_id)
        if idx == -1:
            raise ValueError("Reserva no encontrada.")
        # Elimina la reserva y persiste
        del self.reservations[idx]
        self.persistence.save_reservations(self.reservations)

    # ------------------------------
    # Guardar manualmente
    # ------------------------------
    def save_all(self) -> None:
        # Método de conveniencia para forzar guardado desde fuera.
        self.persistence.save_reservations(self.reservations)