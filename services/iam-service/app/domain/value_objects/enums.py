import enum


class Rol(enum.Enum):
    TURISTA = "Turista"
    PRESTADOR = "Prestador"
    ENTIDAD = "Entidad"
    ADMIN = "Admin"


class TipoDocumento(enum.Enum):
    RNT = "RNT"
    RUT = "RUT"


class EstadoDocumento(enum.Enum):
    PENDIENTE = "Pendiente"
    APROBADO = "Aprobado"
    RECHAZADO = "Rechazado"


class ResultadoAuditoria(enum.Enum):
    EXITO = "Exito"
    DENEGADO = "Denegado"
    ERROR = "Error"
