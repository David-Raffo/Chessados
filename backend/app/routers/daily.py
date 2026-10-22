"""Desafíos diarios: puzzle del día y la mejor jugada en tus propias partidas."""

import hashlib

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..db import get_db
from ..models import DailyChallenge, Game, GameAnalysis, Puzzle, User
from ..services import today
from .puzzles import puzzle_out

router = APIRouter(prefix="/api/daily", tags=["desafíos"])

KINDS = ("puzzle", "own-game")


def _seed(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:12], 16)


def daily_puzzle(db: Session) -> Puzzle | None:
    """El mismo para todos los usuarios de la instalación: popular y de dificultad media."""
    base = select(Puzzle).where(
        Puzzle.popularity >= 93, Puzzle.nb_plays >= 3000, Puzzle.rating.between(1300, 1900)
    )
    n = db.scalar(select(func.count()).select_from(base.subquery()))
    if not n:
        return None
    return db.scalars(base.order_by(Puzzle.id).offset(_seed(today().isoformat()) % n).limit(1)).first()


def own_position(db: Session, user: User) -> dict | None:
    rows = db.execute(
        select(GameAnalysis, Game)
        .join(Game, Game.id == GameAnalysis.game_id)
        .where(
            Game.user_id == user.id,
            GameAnalysis.is_user_move.is_(True),
            GameAnalysis.classification.in_(["mistake", "blunder"]),
            GameAnalysis.best_uci.isnot(None),
        )
        .order_by(Game.played_at.desc(), GameAnalysis.ply)
        .limit(60)
    ).all()
    if not rows:
        return None
    a, g = rows[_seed(f"{user.id}-{today().isoformat()}") % len(rows)]
    return {
        "game_id": g.id, "ply": a.ply, "fen": a.fen_before, "best_uci": a.best_uci, "best_san": a.best_san,
        "played_san": a.san, "user_color": g.user_color, "classification": a.classification,
    }


@router.get("")
def get_daily(user: User = Depends(current_user), db: Session = Depends(get_db)):
    done = {
        c.kind: {"success": c.success, "score": c.score}
        for c in db.scalars(select(DailyChallenge).where(DailyChallenge.user_id == user.id, DailyChallenge.day == today()))
    }
    p = daily_puzzle(db)
    return {
        "day": today().isoformat(),
        "puzzle": puzzle_out(p) if p else None,
        "own": own_position(db, user),
        "done": done,
    }


class DoneIn(BaseModel):
    success: bool
    score: int = Field(default=0, ge=0, le=1000)


@router.post("/{kind}")
def complete(kind: str, body: DoneIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if kind not in KINDS:
        raise HTTPException(404, "Desafío desconocido")
    row = db.scalars(select(DailyChallenge).where(
        DailyChallenge.user_id == user.id, DailyChallenge.day == today(), DailyChallenge.kind == kind)).first()
    if row is None:
        db.add(DailyChallenge(user_id=user.id, day=today(), kind=kind, success=body.success, score=body.score))
    db.commit()
    return {"ok": True}
