from fastapi import APIRouter

router = APIRouter(tags=["Operación"])


@router.get("/health")
def health() -> dict[str, str]:
    """Sonda de Kubernetes. En la Fase 1 comprobará también PostgreSQL y Valkey."""
    return {"status": "ok"}
