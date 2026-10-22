from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import create_token, current_user, hash_password, verify_password
from ..config import DEFAULT_SPLIT, TIME_AREAS
from ..db import get_db
from ..models import User
from ..services import seed_ratings

router = APIRouter(prefix="/api", tags=["usuarios"])


# Validación laxa a propósito: en una instalación casera vale cualquier "algo@algo"
EMAIL = r"^[^@\s]+@[^@\s]+$"


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(pattern=EMAIL, max_length=200)
    password: str = Field(min_length=6, max_length=200)
    level: int = Field(default=1200, ge=400, le=2500)


class LoginIn(BaseModel):
    email: str = Field(max_length=200)
    password: str


class SettingsIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    weekly_hours: float | None = Field(default=None, ge=1, le=60)
    target_split: dict[str, float] | None = None
    review_lock: bool | None = None
    ladder_elo: int | None = Field(default=None, ge=400, le=3000)
    lichess_username: str | None = None
    chesscom_username: str | None = None


def user_out(u: User) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "weekly_hours": u.weekly_hours,
        "target_split": {**DEFAULT_SPLIT, **(u.target_split or {})},
        "ladder_elo": u.ladder_elo,
        "review_lock": u.review_lock,
        "lichess_username": u.lichess_username,
        "chesscom_username": u.chesscom_username,
        "endgame_boost_until": u.endgame_boost_until.isoformat() if u.endgame_boost_until else None,
    }


@router.post("/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(func.count()).select_from(User).where(User.email == email)):
        raise HTTPException(400, "Ya existe una cuenta con ese email")
    user = User(
        name=body.name.strip(),
        email=email,
        password_hash=hash_password(body.password),
        ladder_elo=max(800, min(2400, body.level)),
        target_split=dict(DEFAULT_SPLIT),
    )
    db.add(user)
    db.flush()
    seed_ratings(db, user.id, body.level)
    db.commit()
    return {"token": create_token(user.id), "user": user_out(user)}


@router.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.email == body.email.lower())).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Email o contraseña incorrectos")
    return {"token": create_token(user.id), "user": user_out(user)}


@router.get("/me")
def me(user: User = Depends(current_user)):
    return user_out(user)


@router.patch("/me")
def update_me(body: SettingsIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    if "target_split" in data:
        split = {a: float(data["target_split"].get(a, 0)) for a in TIME_AREAS}
        if abs(sum(split.values()) - 100) > 0.5 or any(v < 0 for v in split.values()):
            raise HTTPException(400, "El reparto debe sumar 100%")
        data["target_split"] = split
    for key, value in data.items():
        if key in ("lichess_username", "chesscom_username"):
            value = (value or "").strip() or None
        setattr(user, key, value)
    db.commit()
    return user_out(user)
