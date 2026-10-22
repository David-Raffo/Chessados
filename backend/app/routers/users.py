import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from ..auth import create_token, current_user, hash_password, verify_password
from ..config import DEFAULT_SPLIT, TIME_AREAS
from ..db import get_db
from ..models import Invite, User
from ..services import seed_ratings

router = APIRouter(prefix="/api", tags=["usuarios"])


# Letras (con acentos), números, punto, guion y guion bajo
USERNAME = re.compile(r"[\w.-]{3,30}")

INVITE_LIMIT = 10  # invitaciones por cuenta; el administrador no tiene límite
# Sin caracteres que se confunden al copiarlos a mano (0/O, 1/I/L)
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


class RegisterIn(BaseModel):
    username: str
    password: str = Field(max_length=200)
    level: int = Field(default=1200, ge=400, le=2500)
    invite_code: str | None = Field(default=None, max_length=20)

    @field_validator("username")
    @classmethod
    def valid_username(cls, v: str) -> str:
        v = v.strip()
        if not USERNAME.fullmatch(v):
            raise ValueError("El usuario debe tener de 3 a 30 letras, números, puntos, guiones o guiones bajos")
        return v

    @field_validator("password")
    @classmethod
    def valid_password(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres")
        return v


class LoginIn(BaseModel):
    username: str = Field(max_length=30)
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
        "username": u.username,
        "weekly_hours": u.weekly_hours,
        "target_split": {**DEFAULT_SPLIT, **(u.target_split or {})},
        "ladder_elo": u.ladder_elo,
        "review_lock": u.review_lock,
        "lichess_username": u.lichess_username,
        "chesscom_username": u.chesscom_username,
        "endgame_boost_until": u.endgame_boost_until.isoformat() if u.endgame_boost_until else None,
        "is_admin": u.is_admin,
    }


def normalize_code(code: str) -> str:
    """Admite el código con o sin guion y en minúsculas: ABCD-EFGH."""
    raw = re.sub(r"[^A-Za-z0-9]", "", code).upper()
    return f"{raw[:4]}-{raw[4:]}" if len(raw) == 8 else raw


def new_code(db: Session) -> str:
    while True:
        raw = "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))
        code = f"{raw[:4]}-{raw[4:]}"
        if not db.scalar(select(func.count()).select_from(Invite).where(Invite.code == code)):
            return code


@router.get("/auth/setup")
def setup(db: Session = Depends(get_db)):
    """La primera cuenta de la instalación no necesita invitación (y será la de administrador)."""
    return {"first_account": not db.scalar(select(func.count()).select_from(User))}


@router.post("/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    username = body.username.strip().lower()
    # Serializa los registros: evita dos «primeras cuentas» o dos usos del mismo código
    db.execute(text("SELECT pg_advisory_xact_lock(4243)"))
    first = not db.scalar(select(func.count()).select_from(User))
    invite = None
    if not first:
        code = normalize_code(body.invite_code or "")
        if not code:
            raise HTTPException(400, "Necesitas un código de invitación para crear una cuenta")
        invite = db.scalars(select(Invite).where(Invite.code == code)).first()
        if invite is None:
            raise HTTPException(400, "Ese código de invitación no existe")
        if invite.used_by is not None:
            raise HTTPException(400, "Ese código de invitación ya se ha usado")
    if db.scalar(select(func.count()).select_from(User).where(User.username == username)):
        raise HTTPException(400, "Ese nombre de usuario ya está en uso")
    user = User(
        name=body.username.strip(),
        username=username,
        password_hash=hash_password(body.password),
        ladder_elo=max(800, min(2400, body.level)),
        target_split=dict(DEFAULT_SPLIT),
        is_admin=first,
        invited_by=invite.created_by if invite else None,
    )
    db.add(user)
    db.flush()
    if invite:
        invite.used_by = user.id
        invite.used_at = datetime.now(timezone.utc)
    seed_ratings(db, user.id, body.level)
    db.commit()
    return {"token": create_token(user.id), "user": user_out(user)}


@router.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.username == body.username.strip().lower())).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Usuario o contraseña incorrectos")
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


# --- Invitaciones ------------------------------------------------------------


def invites_out(db: Session, user: User) -> dict:
    rows = db.execute(
        select(Invite, User.name)
        .outerjoin(User, User.id == Invite.used_by)
        .where(Invite.created_by == user.id)
        .order_by(Invite.created_at.desc())
    ).all()
    return {
        "limit": None if user.is_admin else INVITE_LIMIT,
        "created": len(rows),
        "codes": [
            {
                "code": inv.code,
                "created_at": inv.created_at.isoformat(),
                "used": inv.used_by is not None,
                "used_by": name,
                "used_at": inv.used_at.isoformat() if inv.used_at else None,
            }
            for inv, name in rows
        ],
    }


@router.get("/invites")
def list_invites(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return invites_out(db, user)


@router.post("/invites")
def create_invite(user: User = Depends(current_user), db: Session = Depends(get_db)):
    created = db.scalar(select(func.count()).select_from(Invite).where(Invite.created_by == user.id))
    if not user.is_admin and created >= INVITE_LIMIT:
        raise HTTPException(400, f"Ya has creado tus {INVITE_LIMIT} invitaciones. Anula alguna sin usar para crear otra.")
    db.add(Invite(code=new_code(db), created_by=user.id))
    db.commit()
    return invites_out(db, user)


@router.delete("/invites/{code}")
def revoke_invite(code: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    invite = db.scalars(select(Invite).where(Invite.code == normalize_code(code), Invite.created_by == user.id)).first()
    if invite is None:
        raise HTTPException(404, "Invitación no encontrada")
    if invite.used_by is not None:
        raise HTTPException(400, "Esa invitación ya se usó y no se puede anular")
    db.delete(invite)
    db.commit()
    return invites_out(db, user)
