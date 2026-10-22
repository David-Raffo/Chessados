"""Lógica compartida: ratings Glicko-2, tiempo por área, rachas y reparto objetivo."""

import os
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import glicko2
from .config import DEFAULT_SPLIT, RATING_AREAS, TIME_AREAS
from .models import DailyChallenge, Rating, TrainingSession, User

TZ_NAME = os.getenv("APP_TIMEZONE", "Europe/Madrid")
TZ = ZoneInfo(TZ_NAME)


def today() -> date:
    return datetime.now(TZ).date()


def local_midnight(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=TZ)


def week_start(d: date | None = None) -> date:
    d = d or today()
    return d - timedelta(days=d.weekday())


# --- Ratings ---------------------------------------------------------------


def current_rating(db: Session, user_id: int, area: str) -> tuple[float, float, float]:
    row = db.scalars(
        select(Rating)
        .where(Rating.user_id == user_id, Rating.area == area)
        .order_by(Rating.created_at.desc(), Rating.id.desc())
        .limit(1)
    ).first()
    if row is None:
        return glicko2.DEFAULT_RATING, glicko2.DEFAULT_RD, glicko2.DEFAULT_VOL
    return row.rating, row.rd, row.volatility


def all_ratings(db: Session, user_id: int) -> dict[str, dict]:
    out = {}
    for area in RATING_AREAS:
        r, rd, _ = current_rating(db, user_id, area)
        out[area] = {"rating": round(r), "rd": round(rd), "provisional": rd > 110}
    return out


def apply_result(
    db: Session, user_id: int, area: str, opp_rating: float, opp_rd: float, score: float
) -> tuple[float, float]:
    r, rd, vol = current_rating(db, user_id, area)
    nr, nrd, nvol = glicko2.update(r, rd, vol, opp_rating, opp_rd, score)
    db.add(Rating(user_id=user_id, area=area, rating=nr, rd=nrd, volatility=nvol))
    return r, nr


def seed_ratings(db: Session, user_id: int, level: int) -> None:
    for area in RATING_AREAS:
        db.add(Rating(user_id=user_id, area=area, rating=level, rd=250, volatility=glicko2.DEFAULT_VOL))


# --- Tiempo ----------------------------------------------------------------


def _local_day(col):
    return func.date(func.timezone(TZ_NAME, col))


def seconds_by_area(db: Session, user_id: int, since: date, until: date | None = None) -> dict[str, int]:
    q = select(TrainingSession.area, func.coalesce(func.sum(TrainingSession.active_seconds), 0)).where(
        TrainingSession.user_id == user_id, TrainingSession.started_at >= local_midnight(since)
    )
    if until:
        q = q.where(TrainingSession.started_at < local_midnight(until))
    rows = db.execute(q.group_by(TrainingSession.area)).all()
    out = {a: 0 for a in TIME_AREAS}
    for area, secs in rows:
        out[area] = out.get(area, 0) + int(secs)
    return out


def seconds_by_day(db: Session, user_id: int, since: date) -> dict[date, int]:
    day = _local_day(TrainingSession.started_at)
    rows = db.execute(
        select(day, func.sum(TrainingSession.active_seconds))
        .where(TrainingSession.user_id == user_id, TrainingSession.started_at >= local_midnight(since))
        .group_by(day)
    ).all()
    return {d: int(s) for d, s in rows}


def streak(db: Session, user_id: int) -> int:
    days = seconds_by_day(db, user_id, today() - timedelta(days=400))
    active = {d for d, s in days.items() if s >= 60}
    # Un desafío diario completado también mantiene la racha
    active |= set(db.scalars(select(DailyChallenge.day).where(DailyChallenge.user_id == user_id)))
    d = today()
    if d not in active:
        d -= timedelta(days=1)  # la racha sigue viva hasta que acabe el día de hoy
    n = 0
    while d in active:
        n += 1
        d -= timedelta(days=1)
    return n


def effective_split(user: User) -> dict[str, float]:
    split = {**DEFAULT_SPLIT, **(user.target_split or {})}
    if user.endgame_boost_until and user.endgame_boost_until >= today() and split["endgames"] < 25:
        # Regla 3 del entrenador: finales al 25% durante dos semanas, el resto se reescala
        rest = sum(v for k, v in split.items() if k != "endgames") or 1
        split = {k: (25 if k == "endgames" else v * 75 / rest) for k, v in split.items()}
    return split
