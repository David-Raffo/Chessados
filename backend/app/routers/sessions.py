from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import current_user
from ..config import TIME_AREAS
from ..db import get_db
from ..models import TrainingSession, User

router = APIRouter(prefix="/api/sessions", tags=["tiempo"])


class StartIn(BaseModel):
    area: str
    activity: str = Field(max_length=20)
    ref_id: str | None = None


class BeatIn(BaseModel):
    active_seconds: int = Field(ge=0, le=6 * 3600)


@router.post("")
def start(body: StartIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.area not in TIME_AREAS:
        raise HTTPException(400, "Área desconocida")
    s = TrainingSession(user_id=user.id, area=body.area, activity=body.activity, ref_id=body.ref_id)
    db.add(s)
    db.commit()
    return {"id": s.id}


@router.post("/{session_id}/beat")
def beat(session_id: int, body: BeatIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """El cliente envía el total de segundos activos (solo cuenta con interacción en los últimos 2 min)."""
    s = db.get(TrainingSession, session_id)
    if not s or s.user_id != user.id:
        raise HTTPException(404, "Sesión no encontrada")
    # El total solo puede crecer y nunca más que el tiempo real transcurrido
    elapsed = (datetime.now(timezone.utc) - s.started_at).total_seconds() + 5
    s.active_seconds = int(max(s.active_seconds, min(body.active_seconds, elapsed)))
    s.ended_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
