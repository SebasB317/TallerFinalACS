from fastapi import APIRouter, Depends

from app.domain.entities.user import User
from app.presentation.deps import get_current_user

router = APIRouter(tags=["analysis"])


@router.get("/analyze")
def analyze_placeholder(current: User = Depends(get_current_user)) -> dict[str, str]:
    """Endpoint protegido de ejemplo (Historia #1). En historias siguientes procesará textos."""
    return {"status": "ok", "message": f"Hola usuario {current.email.value}, endpoint protegido."}
