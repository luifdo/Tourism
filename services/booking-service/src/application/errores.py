"""Errores de la capa de aplicación (códigos del contrato booking.yaml)."""

from domain.errores import ErrorDominio


class NoEncontrado(ErrorDominio):
    codigo = "NO_ENCONTRADO"


class RolNoPermitido(ErrorDominio):
    codigo = "ROL_NO_PERMITIDO"


class ReservaDuplicada(ErrorDominio):
    codigo = "RESERVA_DUPLICADA"


class DiaExistente(ErrorDominio):
    codigo = "DIA_EXISTENTE"


class VersionDistinta(ErrorDominio):
    codigo = "VERSION_DISTINTA"

    def __init__(self, mensaje: str, version_actual: int):
        super().__init__(mensaje)
        self.version_actual = version_actual


class FaltaIfMatch(ErrorDominio):
    codigo = "FALTA_IF_MATCH"
