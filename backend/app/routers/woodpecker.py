"""Método Woodpecker: el mismo bloque de puzzles en ciclos cada vez más cortos."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..db import get_db
from ..models import Puzzle, PuzzleAttempt, User, WoodpeckerCycle, WoodpeckerSet
from ..services import current_rating
from .puzzles import puzzle_out

router = APIRouter(prefix="/api/woodpecker", tags=["woodpecker"])


def active_set(db: Session, user: User) -> WoodpeckerSet | None:
    return db.scalars(
        select(WoodpeckerSet).where(WoodpeckerSet.user_id == user.id, WoodpeckerSet.active.is_(True))
        .order_by(WoodpeckerSet.created_at.desc()).limit(1)
    ).first()


def set_out(s: WoodpeckerSet) -> dict:
    size = len(s.puzzle_ids)
    return {
        "id": s.id,
        "size": size,
        "created_at": s.created_at.isoformat(),
        "cycles": [
            {
                "number": c.number,
                "position": c.position,
                "solved": c.solved,
                "accuracy": round(100 * c.solved / c.position) if c.position else None,
                "seconds": round(c.seconds),
                "target_days": c.target_days,
                "started_at": c.started_at.isoformat(),
                "finished_at": c.finished_at.isoformat() if c.finished_at else None,
                "days": max(1, ((c.finished_at or datetime.now(timezone.utc)) - c.started_at).days + 1),
            }
            for c in s.cycles
        ],
    }


@router.get("")
def get_set(user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = active_set(db, user)
    return set_out(s) if s else None


class CreateIn(BaseModel):
    size: int = Field(ge=20, le=300)


@router.post("")
def create_set(body: CreateIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    rating = current_rating(db, user.id, "tactics")[0]
    # Puzzles algo por debajo de tu nivel: el método busca automatizar patrones, no sufrir
    ids = list(db.scalars(
        select(Puzzle.id)
        .where(Puzzle.rating.between(rating - 250, rating + 50), Puzzle.popularity >= 85)
        .order_by(func.random()).limit(body.size)
    ))
    if len(ids) < body.size:
        ids += list(db.scalars(
            select(Puzzle.id).where(Puzzle.id.notin_(ids)).order_by(func.abs(Puzzle.rating - rating))
            .limit(body.size - len(ids))
        ))
    for old in db.scalars(select(WoodpeckerSet).where(WoodpeckerSet.user_id == user.id, WoodpeckerSet.active.is_(True))):
        old.active = False
    s = WoodpeckerSet(user_id=user.id, puzzle_ids=ids, active=True)
    db.add(s)
    db.flush()
    # Primer ciclo: unos 25 puzzles al día; cada ciclo siguiente, la mitad de días
    db.add(WoodpeckerCycle(set_id=s.id, number=1, target_days=max(2, round(body.size / 25))))
    db.commit()
    db.refresh(s)
    return set_out(s)


@router.delete("")
def stop_set(user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = active_set(db, user)
    if s:
        s.active = False
        db.commit()
    return {"ok": True}


@router.get("/next")
def next_puzzle(user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = active_set(db, user)
    if not s:
        raise HTTPException(404, "No tienes un bloque Woodpecker activo")
    cycle = s.cycles[-1]
    p = db.get(Puzzle, s.puzzle_ids[cycle.position])
    return {**puzzle_out(p), "cycle": cycle.number, "index": cycle.position, "size": len(s.puzzle_ids)}


class AttemptIn(BaseModel):
    puzzle_id: str
    solved: bool
    seconds: float = Field(ge=0, le=3600)


@router.post("/attempt")
def attempt(body: AttemptIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = active_set(db, user)
    if not s:
        raise HTTPException(404, "No tienes un bloque Woodpecker activo")
    cycle = s.cycles[-1]
    if s.puzzle_ids[cycle.position] != body.puzzle_id:
        raise HTTPException(409, "Ese puzzle no es el siguiente del ciclo")
    db.add(PuzzleAttempt(user_id=user.id, puzzle_id=body.puzzle_id, solved=body.solved,
                         seconds=body.seconds, mode="woodpecker"))
    cycle.position += 1
    cycle.solved += int(body.solved)
    cycle.seconds += body.seconds
    finished = None
    if cycle.position >= len(s.puzzle_ids):
        cycle.finished_at = datetime.now(timezone.utc)
        finished = cycle.number
        db.add(WoodpeckerCycle(set_id=s.id, number=cycle.number + 1, target_days=max(1, cycle.target_days // 2)))
    db.commit()
    db.refresh(s)
    return {**set_out(s), "finished_cycle": finished}
