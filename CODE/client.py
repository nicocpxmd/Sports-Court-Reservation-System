"""
client.py
----------

Clase que representa a un cliente del sistema de reservas.
Se encarga de validar toda la información personal del usuario
(nombre, documento, teléfono, correo) al momento de crear el objeto.

Esta clase NO tiene dependencias gráficas ni de JSON.
"""

import re

class Client:
    """
    Representa un cliente con sus datos personales.
    Se valida toda la información al inicializar el objeto.
    """

    NOMBRE_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\- ]+$")
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    TELEFONO_REGEX = re.compile(r"^\+?\d{6,15}$")

    def __init__(self, nombre: str, documento: str, telefono: str, email: str):
        self.nombre = self._validar_nombre(nombre)
        self.documento = self._validar_documento(documento)
        self.telefono = self._validar_telefono(telefono)
        self.email = self._validar_email(email)

    # --------------------------------------------------
    # Métodos de validación individuales
    # --------------------------------------------------
    def _validar_nombre(self, nombre: str) -> str:
        if not nombre or not self.NOMBRE_REGEX.fullmatch(nombre.strip()):
            raise ValueError("El nombre solo puede contener letras y espacios.")
        return nombre.strip()

    def _validar_documento(self, doc: str) -> str:
        if not doc.isdigit():
            raise ValueError("El documento debe contener solo números.")
        return doc.strip()

    def _validar_telefono(self, tel: str) -> str:
        tel = re.sub(r"[ \-()]", "", tel)
        if not self.TELEFONO_REGEX.fullmatch(tel):
            raise ValueError("Teléfono inválido. Debe tener entre 6 y 15 dígitos.")
        return tel

    def _validar_email(self, email: str) -> str:
        if not self.EMAIL_REGEX.fullmatch(email):
            raise ValueError("Correo electrónico inválido.")
        return email.strip()

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "documento": self.documento,
            "telefono": self.telefono,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def __repr__(self):
        return f"Client({self.nombre}, {self.documento})"
