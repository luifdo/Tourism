from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.errors import DatoInvalido
from app.domain.value_objects.catalogos import NivelAlerta
from app.domain.value_objects.texto_traducido import TextoTraducido


@dataclass(kw_only=True)
class AlertaOficial:
    """Aviso oficial de la Entidad sobre un servicio o sobre una zona completa (UC26)."""

    id: UUID
    nivel: NivelAlerta
    mensaje: TextoTraducido
    entidad_usuario_id: UUID
    fecha_expiracion: datetime
    creada_en: datetime
    servicio_id: UUID | None = None
    zona_id: UUID | None = None
    activa: bool = True

    @classmethod
    def publicar(
        cls,
        nivel: NivelAlerta,
        mensaje: TextoTraducido,
        entidad_usuario_id: UUID,
        fecha_expiracion: datetime,
        ahora: datetime,
        servicio_id: UUID | None = None,
        zona_id: UUID | None = None,
    ) -> "AlertaOficial":
        if (servicio_id is None) == (zona_id is None):
            raise DatoInvalido(campo="servicio_id|zona", regla="exactamente_uno")
        if fecha_expiracion <= ahora:
            raise DatoInvalido(campo="fecha_expiracion", regla="futura")
        return cls(
            id=uuid4(),
            nivel=nivel,
            mensaje=mensaje,
            entidad_usuario_id=entidad_usuario_id,
            fecha_expiracion=fecha_expiracion,
            creada_en=ahora,
            servicio_id=servicio_id,
            zona_id=zona_id,
        )

    def vigente(self, ahora: datetime) -> bool:
        return self.activa and self.fecha_expiracion > ahora

    def desactivar(self) -> None:
        self.activa = False
