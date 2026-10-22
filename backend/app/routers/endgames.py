from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..db import get_db
from ..lessons import BY_ID, LESSONS
from ..models import EndgameAttempt, ReviewItem, User
from ..services import apply_result, current_rating, today

router = APIRouter(prefix="/api/endgames", tags=["finales"])

LESSON_RD = 60.0
REVIEW_STEPS = [1, 3, 7, 21]


@router.get("")
def list_lessons(user: User = Depends(current_user), db: Session = Depends(get_db)):
    stats = {
        lid: (n, ok)
        for lid, n, ok in db.execute(
            select(
                EndgameAttempt.lesson_id,
                func.count(),
                func.sum(case((EndgameAttempt.success, 1), else_=0)),
            )
            .where(EndgameAttempt.user_id == user.id)
            .group_by(EndgameAttempt.lesson_id)
        ).all()
    }
    due = {
        r.ref_id: r.due_date
        for r in db.scalars(select(ReviewItem).where(ReviewItem.user_id == user.id, ReviewItem.kind == "endgame"))
    }
    out = []
    for lesson in LESSONS:
        n, ok = stats.get(lesson["id"], (0, 0))
        d = due.get(lesson["id"])
        out.append({
            **lesson,
            "attempts": n,
            "successes": int(ok or 0),
            "due": d is not None and d <= today(),
            "next_review": d.isoformat() if d else None,
        })
    return {"lessons": out, "rating": round(current_rating(db, user.id, "endgames")[0])}


class AttemptIn(BaseModel):
    success: bool
    seconds: float = Field(ge=0, le=7200)
    moves: int = Field(ge=0, le=500)


@router.post("/{lesson_id}/attempt")
def attempt(lesson_id: str, body: AttemptIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = BY_ID.get(lesson_id)
    if not lesson:
        raise HTTPException(404, "Lección no encontrada")
    db.add(EndgameAttempt(user_id=user.id, lesson_id=lesson_id, success=body.success,
                          seconds=body.seconds, moves=body.moves))
    before, after = apply_result(db, user.id, "endgames", lesson["rating"], LESSON_RD, 1.0 if body.success else 0.0)

    # Repetición espaciada: las posiciones se repasan a los 1, 3, 7 y 21 días
    item = db.scalars(select(ReviewItem).where(
        ReviewItem.user_id == user.id, ReviewItem.kind == "endgame", ReviewItem.ref_id == lesson_id
    )).first()
    if item is None:
        item = ReviewItem(user_id=user.id, kind="endgame", ref_id=lesson_id, reps=-1)
        db.add(item)
    if body.success:
        item.reps = min(item.reps + 1, len(REVIEW_STEPS) - 1)
    else:
        item.reps = 0
    item.interval = REVIEW_STEPS[max(item.reps, 0)]
    item.due_date = today() + timedelta(days=item.interval)
    db.commit()
    return {"rating_before": round(before), "rating_after": round(after), "next_review": item.due_date.isoformat()}
