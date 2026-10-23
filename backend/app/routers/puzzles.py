import random
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import ARRAY, Text, cast, exists, func, literal_column, select, tablesample
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import array, insert as pg_insert
from sqlalchemy.orm import Session

from ..auth import current_user
from ..db import get_db
from ..models import Puzzle, PuzzleAssignment, PuzzleAttempt, ReviewItem, RushRun, User
from ..services import apply_result, current_rating, today

router = APIRouter(prefix="/api/puzzles", tags=["puzzles"])

REVIEW_STEPS = [1, 3, 7, 21]  # días: cada fallo vuelve a aparecer a los 1, 3, 7 y 21 días


def puzzle_out(p: Puzzle) -> dict:
    return {
        "id": p.id,
        "fen": p.fen,
        "moves": p.moves.split(),
        "rating": p.rating,
        "themes": p.themes.split(),
        "opening": p.opening_tags,
    }


def _theme_filter(theme: str, indexed: bool = True):
    """Filtro por tema.

    indexed=True usa el índice GIN ix_puzzles_themes: ideal para temas raros o rangos amplios.
    indexed=False comprueba el texto puzzle a puzzle: más rápido en bandas de ELO estrechas con temas
    frecuentes («final», «horquilla»), donde el índice tendría que recorrer cientos de miles de entradas.
    """
    if not indexed:
        return (" " + Puzzle.themes + " ").like(f"% {theme} %")
    # El separador va como constante en el SQL para que la expresión coincida con la del índice
    themes = func.string_to_array(Puzzle.themes, literal_column("' '"))
    return themes.op("@>")(cast(array([theme]), ARRAY(Text)))


@router.get("/count")
def count(db: Session = Depends(get_db)):
    return {"count": db.scalar(select(func.count()).select_from(Puzzle))}


@router.get("/next")
def next_puzzle(
    theme: str | None = None,
    area: str = "tactics",
    review: bool = False,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if review:
        item = db.scalars(
            select(ReviewItem)
            .where(ReviewItem.user_id == user.id, ReviewItem.kind == "puzzle", ReviewItem.due_date <= today())
            .order_by(ReviewItem.due_date, ReviewItem.id)
            .limit(1)
        ).first()
        if item and (p := db.get(Puzzle, item.ref_id)):
            return {**puzzle_out(p), "review": True}
        raise HTTPException(404, "No tienes puzzles pendientes de repaso")

    # Si ya tenías un puzzle asignado con este filtro y no lo has terminado, sigue siendo el mismo
    key = f"{area}|{theme or ''}"
    assigned = db.scalars(select(PuzzleAssignment).where(
        PuzzleAssignment.user_id == user.id, PuzzleAssignment.filter_key == key)).first()
    if assigned:
        p = db.get(Puzzle, assigned.puzzle_id)
        done = db.scalar(select(func.count()).select_from(PuzzleAttempt).where(
            PuzzleAttempt.user_id == user.id, PuzzleAttempt.puzzle_id == assigned.puzzle_id))
        if p and not done:
            return {**puzzle_out(p), "review": False}

    rating, _, _ = current_rating(db, user.id, "endgames" if area == "endgames" else "tactics")
    attempted = exists().where(PuzzleAttempt.user_id == user.id, PuzzleAttempt.puzzle_id == Puzzle.id)
    # Con un millón de puzzles, sortear entre todos los de tu franja de ELO es lento: se elige un punto
    # al azar de la franja (±100) y se sortea en una banda estrecha a su alrededor, que se ensancha
    # si no hay puzzles (temas raros, niveles extremos).
    center = rating + random.uniform(-100, 100)
    for width in (15, 50, 150, 400, 3000):
        q = select(Puzzle).where(
            Puzzle.rating.between(center - width, center + width), ~attempted
        )
        if theme:
            q = q.where(_theme_filter(theme, indexed=width > 50))
        p = db.scalars(q.order_by(func.random()).limit(1)).first()
        if p:
            if assigned:
                assigned.puzzle_id = p.id
                db.commit()
                return {**puzzle_out(p), "review": False}
            # Dos peticiones a la vez (recargas rápidas) pueden asignar a la vez: gana la primera
            # y la otra devuelve ese mismo puzzle
            db.execute(
                pg_insert(PuzzleAssignment)
                .values(user_id=user.id, filter_key=key, puzzle_id=p.id)
                .on_conflict_do_nothing(index_elements=["user_id", "filter_key"])
            )
            db.commit()
            won = db.scalar(select(PuzzleAssignment.puzzle_id).where(
                PuzzleAssignment.user_id == user.id, PuzzleAssignment.filter_key == key))
            if won and won != p.id and (other := db.get(Puzzle, won)):
                p = other
            return {**puzzle_out(p), "review": False}
    raise HTTPException(404, "No hay puzzles disponibles. ¿Se ha ejecutado el importador?")


class AttemptIn(BaseModel):
    solved: bool
    seconds: float = Field(ge=0, le=3600)
    mode: str = "normal"
    area: str = "tactics"


def _update_review_queue(db: Session, user_id: int, puzzle_id: str, solved: bool) -> None:
    item = db.scalars(
        select(ReviewItem).where(
            ReviewItem.user_id == user_id, ReviewItem.kind == "puzzle", ReviewItem.ref_id == puzzle_id
        )
    ).first()
    if not solved:
        if item is None:
            item = ReviewItem(user_id=user_id, kind="puzzle", ref_id=puzzle_id)
            db.add(item)
        item.interval, item.reps = REVIEW_STEPS[0], 0
        item.ease = max(1.3, (item.ease or 2.5) - 0.2)
        item.due_date = today() + timedelta(days=REVIEW_STEPS[0])
    elif item is not None:
        item.reps += 1
        if item.reps >= len(REVIEW_STEPS):
            db.delete(item)  # aprendido
        else:
            item.interval = REVIEW_STEPS[item.reps]
            item.due_date = today() + timedelta(days=item.interval)


@router.post("/{puzzle_id}/attempt")
def attempt(puzzle_id: str, body: AttemptIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = db.get(Puzzle, puzzle_id)
    if not p:
        raise HTTPException(404, "Puzzle no encontrado")
    db.add(PuzzleAttempt(user_id=user.id, puzzle_id=p.id, solved=body.solved, seconds=body.seconds, mode=body.mode))
    area = "endgames" if body.area == "endgames" else "tactics"
    # Los repasos no mueven el rating: ya contaron la primera vez
    before = after = current_rating(db, user.id, area)[0]
    if body.mode == "normal":
        before, after = apply_result(db, user.id, area, p.rating, p.rating_dev, 1.0 if body.solved else 0.0)
    _update_review_queue(db, user.id, p.id, body.solved)
    db.commit()
    return {"area": area, "rating_before": round(before), "rating_after": round(after)}


@router.get("/review/count")
def review_count(user: User = Depends(current_user), db: Session = Depends(get_db)):
    n = db.scalar(
        select(func.count()).select_from(ReviewItem).where(
            ReviewItem.user_id == user.id, ReviewItem.kind == "puzzle", ReviewItem.due_date <= today()
        )
    )
    return {"due": n}


# --- Contrarreloj ----------------------------------------------------------


@router.get("/rush")
def rush_set(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Lista de puzzles cortos con dificultad creciente."""
    tactics = current_rating(db, user.id, "tactics")[0]
    start = max(500, tactics - 550)
    end = start + 1600
    # Muestra aleatoria por bloques (TABLESAMPLE): no hace falta ordenar cientos de miles de filas
    sample = aliased(Puzzle, tablesample(Puzzle.__table__, func.system(3)))
    pool = db.scalars(select(sample).where(sample.rating.between(start, end)).limit(6000)).all()
    if len(pool) < 500:  # base de datos pequeña: muestra completa
        pool = db.scalars(
            select(Puzzle).where(Puzzle.rating.between(start, end)).order_by(func.random()).limit(3000)
        ).all()
    pool = [p for p in pool if len(p.moves.split()) <= 6]
    if not pool:
        raise HTTPException(404, "No hay puzzles disponibles. ¿Se ha ejecutado el importador?")
    by_rating = sorted(pool, key=lambda p: p.rating)
    used: set[str] = set()
    out = []
    for i in range(90):
        target = start + i * 18 if i < 40 else start + 720 + (i - 40) * 15
        candidates = [p for p in by_rating if p.id not in used and abs(p.rating - target) < 120]
        if not candidates:
            candidates = [p for p in by_rating if p.id not in used and p.rating >= target - 50]
        if not candidates:
            break
        p = random.choice(candidates[:12])
        used.add(p.id)
        out.append(puzzle_out(p))
    return {"puzzles": out}


class RushAttempt(BaseModel):
    puzzle_id: str
    solved: bool
    seconds: float = Field(ge=0, le=600)


class RushFinishIn(BaseModel):
    minutes: int = Field(ge=1, le=10)
    score: int = Field(ge=0, le=500)
    attempts: list[RushAttempt] = Field(max_length=500)


@router.post("/rush/finish")
def rush_finish(body: RushFinishIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    best_before = db.scalar(
        select(func.max(RushRun.score)).where(RushRun.user_id == user.id, RushRun.minutes == body.minutes)
    )
    for a in body.attempts:
        p = db.get(Puzzle, a.puzzle_id)
        if not p:
            continue
        db.add(PuzzleAttempt(user_id=user.id, puzzle_id=p.id, solved=a.solved, seconds=a.seconds, mode="rush"))
        apply_result(db, user.id, "rush", p.rating, p.rating_dev, 1.0 if a.solved else 0.0)
    db.add(RushRun(user_id=user.id, minutes=body.minutes, score=body.score))
    db.commit()
    return {
        "best": max(best_before or 0, body.score),
        "is_record": body.score > (best_before or 0),
        "rating": round(current_rating(db, user.id, "rush")[0]),
    }


@router.get("/rush/history")
def rush_history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    runs = db.scalars(
        select(RushRun).where(RushRun.user_id == user.id).order_by(RushRun.created_at.desc()).limit(60)
    ).all()
    best = {
        m: s
        for m, s in db.execute(
            select(RushRun.minutes, func.max(RushRun.score)).where(RushRun.user_id == user.id).group_by(RushRun.minutes)
        ).all()
    }
    return {
        "best": best,
        "runs": [
            {"id": r.id, "minutes": r.minutes, "score": r.score, "date": r.created_at.isoformat()}
            for r in reversed(runs)
        ],
    }
