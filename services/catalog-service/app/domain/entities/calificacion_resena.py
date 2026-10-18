from dataclasses import dataclass
from uuid import UUID

from app.domain.errors import DatoInvalido


@dataclass(kw_only=True)
class CalificacionResena:
    """Puntuación de una reseña publicada (proyección de `resena.publicada`).

    Una fila por reseña: si review-service la vuelve a publicar tras una moderación (UC29),
    se actualiza la misma fila y el promedio no cuenta doble. Las reseñas ocultas siguen
    contando en el promedio; solo dejan de mostrarse en review-service.
    """

    resena_id: UUID
    servicio_id: UUID
    puntuacion: int

    def __post_init__(self) -> None:
        if not 1 <= self.puntuacion <= 5:
            raise DatoInvalido(campo="puntuacion", regla="rango", minimo=1, maximo=5)
