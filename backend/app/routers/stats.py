from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..coach import theme_stats, today_plan, weak_themes
from ..config import RATING_AREAS
from ..db import get_db
from ..models import Game, GameAnalysis, Rating, User
from ..services import (
    TZ,
    all_ratings,
    current_rating,
    local_midnight,
    effective_split,
    seconds_by_area,
    seconds_by_day,
    streak,
    today,
    week_start,
)

router = APIRouter(prefix="/api", tags=["estadísticas"])


def week_targets(user: User) -> dict[str, int]:
    split = effective_split(user)
    total = user.weekly_hours * 3600
    return {a: round(total * pct / 100) for a, pct in split.items()}


@router.get("/stats/overview")
def overview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {
        "ratings": all_ratings(db, user.id),
        "streak": streak(db, user.id),
        "today_seconds": sum(seconds_by_area(db, user.id, today()).values()),
        "week": seconds_by_area(db, user.id, week_start()),
        "week_target": week_targets(user),
        "split": effective_split(user),
    }


@router.get("/stats/progress")
def progress(user: User = Depends(current_user), db: Session = Depends(get_db)):
    # Curvas de ELO: último valor de cada día por área
    history: dict[str, list] = {a: [] for a in RATING_AREAS}
    rows = db.execute(
        select(Rating.area, Rating.created_at, Rating.rating)
        .where(Rating.user_id == user.id)
        .order_by(Rating.created_at, Rating.id)
    ).all()
    per_day: dict[tuple[str, str], float] = {}
    for area, ts, rating in rows:
        per_day[(area, ts.astimezone(TZ).date().isoformat())] = rating
    for (area, day), rating in per_day.items():
        history.setdefault(area, []).append({"date": day, "rating": round(rating)})

    since = today() - timedelta(days=181)
    days = seconds_by_day(db, user.id, since)
    heatmap = [
        {"date": (since + timedelta(days=i)).isoformat(), "seconds": days.get(since + timedelta(days=i), 0)}
        for i in range(182)
    ]

    weeks = []
    ws = week_start()
    for i in range(7, -1, -1):
        start = ws - timedelta(weeks=i)
        weeks.append({"week": start.isoformat(), **seconds_by_area(db, user.id, start, start + timedelta(weeks=1))})

    err_rows = db.execute(
        select(GameAnalysis.phase, GameAnalysis.error_type, GameAnalysis.classification, func.count())
        .join(Game, Game.id == GameAnalysis.game_id)
        .where(
            Game.user_id == user.id,
            GameAnalysis.is_user_move.is_(True),
            GameAnalysis.classification.in_(["mistake", "blunder"]),
        )
        .group_by(GameAnalysis.phase, GameAnalysis.error_type, GameAnalysis.classification)
    ).all()
    by_phase: dict[str, dict] = {p: {"mistake": 0, "blunder": 0} for p in ("opening", "middlegame", "endgame")}
    by_type: dict[str, int] = {}
    for phase, etype, cls, n in err_rows:
        by_phase.setdefault(phase, {"mistake": 0, "blunder": 0})[cls] += n
        if etype:
            by_type[etype] = by_type.get(etype, 0) + n

    return {
        "rating_history": history,
        "heatmap": heatmap,
        "weeks": weeks,
        "week": seconds_by_area(db, user.id, week_start()),
        "week_target": week_targets(user),
        "themes": theme_stats(db, user.id, days=90),
        "weak_themes": weak_themes(db, user.id),
        "errors": {"by_phase": by_phase, "by_type": by_type},
    }


@router.get("/stats/weekly-report")
def weekly_report(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Resumen de la semana: horas frente a objetivo, evolución de cada ELO, temas débiles y consejos."""
    start = local_midnight(week_start())
    elo = {}
    for area in RATING_AREAS:
        now = current_rating(db, user.id, area)[0]
        before = db.scalars(
            select(Rating.rating)
            .where(Rating.user_id == user.id, Rating.area == area, Rating.created_at < start)
            .order_by(Rating.created_at.desc(), Rating.id.desc()).limit(1)
        ).first()
        if before is None:  # cuenta creada esta semana: se compara con el rating inicial
            before = db.scalars(
                select(Rating.rating).where(Rating.user_id == user.id, Rating.area == area)
                .order_by(Rating.created_at, Rating.id).limit(1)
            ).first()
        elo[area] = {"now": round(now), "change": round(now - before) if before is not None else 0}
    plan = today_plan(db, user)
    return {
        "week_start": week_start().isoformat(),
        "week": seconds_by_area(db, user.id, week_start()),
        "week_target": week_targets(user),
        "elo": elo,
        "weak_themes": plan["weak_themes"][:3],
        "tips": [a["text"] for a in plan["advice"]][:3],
    }


@router.get("/coach/today")
def coach_today(user: User = Depends(current_user), db: Session = Depends(get_db)):
    from ..plan import plan_for_today  # import diferido: plan importa routers.daily

    return plan_for_today(db, user)
