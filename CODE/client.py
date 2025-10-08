# Juan David Ocampo Gutierrez
# Nicolás Castro Pacheco
# Michell Valencia Berdugo
# Juan David Rivera Durán

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
    # ------------------------------------------------------------
    # Explicación general:
    # - Esta clase encapsula los datos personales de un usuario
    #   (nombre, documento, teléfono, email).
    # - En el constructor se llama a métodos privados de validación
    #   para garantizar consistencia/integridad.
    # - Se proporciona to_dict / from_dict para serialización sencilla.
    # ------------------------------------------------------------

    # Regex usados para validaciones simples
    NOMBRE_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\- ]+$")
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    TELEFONO_REGEX = re.compile(r"^\+?\d{6,15}$")

    def __init__(self, nombre: str, documento: str, telefono: str, email: str):
        # Al inicializar, se validan y asignan los atributos.
        # Si alguna validación falla, se lanza ValueError (controlado por el caller).
        self.nombre = self._validar_nombre(nombre)
        self.documento = self._validar_documento(documento)
        self.telefono = self._validar_telefono(telefono)
        self.email = self._validar_email(email)

    # --------------------------------------------------
    # Métodos de validación individuales
    # --------------------------------------------------
    def _validar_nombre(self, nombre: str) -> str:
        # Quita espacios alrededor y valida contra NOMBRE_REGEX.
        # Acepta letras (incluyendo acentuadas), apóstrofe, guion y espacios.
        if not nombre or not self.NOMBRE_REGEX.fullmatch(nombre.strip()):
            raise ValueError("El nombre solo puede contener letras y espacios.")
        return nombre.strip()

    def _validar_documento(self, doc: str) -> str:
        # Verifica que el documento contenga solo dígitos.
        # Nota: se acepta como string de números; no se fuerza longitud.
        if not doc.isdigit():
            raise ValueError("El documento debe contener solo números.")
        return doc.strip()

    def _validar_telefono(self, tel: str) -> str:
        # Normaliza teléfono eliminando espacios, guiones y paréntesis.
        # Luego valida con TELEFONO_REGEX que permita + opcional y 6-15 dígitos.
        tel = re.sub(r"[ \-()]", "", tel)
        if not self.TELEFONO_REGEX.fullmatch(tel):
            raise ValueError("Teléfono inválido. Debe tener entre 6 y 15 dígitos.")
        return tel

    def _validar_email(self, email: str) -> str:
        # Validación muy simple de email. No cubre todos los casos RFC,
        # pero es suficiente para validaciones básicas en UI local.
        if not self.EMAIL_REGEX.fullmatch(email):
            raise ValueError("Correo electrónico inválido.")
        return email.strip()

    # --------------------------------------------------
    # Serialización / utilidad
    # --------------------------------------------------
    def to_dict(self) -> dict:
        # Devuelve un dict plano con los campos públicos (útil para persistir).
        return {
            "nombre": self.nombre,
            "documento": self.documento,
            "telefono": self.telefono,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data: dict):
        # Construye Client directamente desde un dict con las mismas keys.
        # IMPORTANTE: asume que el dict tiene las keys requeridas.
        return cls(**data)

    def __repr__(self):
        # Representación compacta para debug/logging.
        return f"Client({self.nombre}, {self.documento})"