import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import current_user
from ..config import MAIA_URL
from ..models import User

router = APIRouter(prefix="/api/maia", tags=["maia"])


class MoveIn(BaseModel):
    fen: str = Field(max_length=100)
    level: int = Field(ge=1100, le=1900)


@router.get("/status")
def status(_: User = Depends(current_user)):
    try:
        r = httpx.get(f"{MAIA_URL}/health", timeout=2)
        r.raise_for_status()
        return {"available": True, "levels": r.json()["levels"]}
    except (httpx.HTTPError, KeyError, ValueError):
        return {"available": False, "levels": []}


@router.post("/move")
def move(body: MoveIn, _: User = Depends(current_user)):
    try:
        # La primera jugada de cada nivel arranca lc0 y carga la red: puede tardar unos segundos
        r = httpx.post(f"{MAIA_URL}/move", json=body.model_dump(), timeout=60)
    except httpx.HTTPError:
        raise HTTPException(503, "El rival Maia no está disponible")
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.json().get("detail", "Error de Maia"))
    return r.json()
