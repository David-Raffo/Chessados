from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from ..auth import current_user
from ..db import get_db
from ..learn import BY_ID, COURSES
from ..models import LessonProgress, User

router = APIRouter(prefix="/api/learn", tags=["aprender"])


def progress_out(p: LessonProgress | None) -> dict:
    if p is None:
        return {"step": 0, "completed": False}
    return {"step": p.step, "completed": p.completed_at is not None}


@router.get("")
def courses(user: User = Depends(current_user), db: Session = Depends(get_db)):
    progress = {p.lesson_id: p for p in db.scalars(select(LessonProgress).where(LessonProgress.user_id == user.id))}
    out = []
    for c in COURSES:
        lessons = []
        for lid, title in c["outline"]:
            lesson = BY_ID.get(lid) if lid else None
            lessons.append({
                "id": lid, "title": lesson["title"] if lesson else title, "available": lesson is not None,
                "summary": lesson["summary"] if lesson else None, "minutes": lesson["minutes"] if lesson else None,
                "progress": progress_out(progress.get(lid)) if lesson else None,
            })
        out.append({"id": c["id"], "title": c["title"], "description": c["description"], "lessons": lessons})
    return {"courses": out}


@router.get("/{lesson_id}")
def lesson(lesson_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = BY_ID.get(lesson_id)
    if not lesson:
        raise HTTPException(404, "Lección no encontrada")
    p = db.scalars(select(LessonProgress).where(
        LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id)).first()
    course = next(c for c in COURSES if c["id"] == lesson["course"])
    return {**lesson, "course_title": course["title"], "progress": progress_out(p)}


class ProgressIn(BaseModel):
    step: int = Field(ge=0, le=100)
    completed: bool = False
    mistakes: int = Field(default=0, ge=0, le=1000)


@router.post("/{lesson_id}/progress")
def save_progress(lesson_id: str, body: ProgressIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = BY_ID.get(lesson_id)
    if not lesson:
        raise HTTPException(404, "Lección no encontrada")
    step = min(body.step, len(lesson["steps"]))
    # Una fila por usuario y lección (dos peticiones a la vez no la duplican)
    db.execute(pg_insert(LessonProgress).values(user_id=user.id, lesson_id=lesson_id, step=0)
               .on_conflict_do_nothing(index_elements=["user_id", "lesson_id"]))
    p = db.scalars(select(LessonProgress).where(
        LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id)).one()
    p.step = 0 if body.completed else step
    if body.completed:
        p.completed_at = p.completed_at or datetime.now(timezone.utc)
        p.best_mistakes = body.mistakes if p.best_mistakes is None else min(p.best_mistakes, body.mistakes)
    db.commit()
    return progress_out(p)
