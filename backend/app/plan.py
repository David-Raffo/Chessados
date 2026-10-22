"""Sesión «Entrenar hoy»: se fija una vez al día y cada paso se completa con actividad real."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .coach import today_plan
from .models import (
    DailyChallenge,
    DailyPlan,
    EndgameAttempt,
    Game,
    RushRun,
    TrainingSession,
    User,
)
from .routers.daily import daily_puzzle, own_position
from .services import local_midnight, today

# Actividades (useActivity en el frontend) que cuentan para cada tipo de paso por tiempo
TIMED = {
    "puzzles": ("tactics", ["puzzles", "review"]),
    "woodpecker": ("tactics", ["woodpecker"]),
    "endgame": ("endgames", None),  # cualquier actividad de finales
    "openings": ("openings", None),
}


def _seconds(db: Session, user: User, area: str, activities: list[str] | None, since) -> int:
    q = select(func.coalesce(func.sum(TrainingSession.active_seconds), 0)).where(
        TrainingSession.user_id == user.id, TrainingSession.area == area, TrainingSession.started_at >= since
    )
    if activities:
        q = q.where(TrainingSession.activity.in_(activities))
    return int(db.scalar(q))


def _progress(db: Session, user: User, step: dict, plan: DailyPlan) -> tuple[float, str, dict]:
    """Devuelve (progreso 0..1, texto, datos extra) de un paso según lo que has hecho hoy."""
    since = local_midnight(today())
    kind = step["kind"]

    if kind in TIMED:
        area, activities = TIMED[kind]
        secs = _seconds(db, user, area, activities, since)
        target = max(60, step["minutes"] * 60)
        if kind == "endgame" and step.get("lesson_id"):
            # Conseguir la lección propuesta también completa el paso
            won = db.scalar(select(func.count()).select_from(EndgameAttempt).where(
                EndgameAttempt.user_id == user.id, EndgameAttempt.lesson_id == step["lesson_id"],
                EndgameAttempt.success.is_(True), EndgameAttempt.created_at >= since))
            if won:
                return 1.0, "Lección conseguida", {"seconds": secs, "target_seconds": target}
        return min(1.0, secs / target), f"{secs // 60} de {step['minutes']} min", {"seconds": secs, "target_seconds": target}

    if kind == "game":
        played = db.scalar(select(func.count()).select_from(Game).where(
            Game.user_id == user.id, Game.source == "app", Game.created_at >= plan.created_at))
        return (1.0, "Jugada", {}) if played else (0.0, "Sin jugar", {})

    if kind == "review":
        if step.get("game_id"):
            g = db.get(Game, step["game_id"])
            done = g is None or g.reviewed
            return (1.0, "Revisada", {}) if done else (0.0, "Sin revisar", {})
        games = db.scalars(select(Game).where(
            Game.user_id == user.id, Game.source == "app", Game.created_at >= plan.created_at)).all()
        if not games:
            return 0.0, "Primero juega la partida", {}
        pending = [g for g in games if not g.reviewed]
        return (0.0, "Sin revisar", {}) if pending else (1.0, "Revisada", {})

    if kind == "rush":
        runs = db.scalar(select(func.count()).select_from(RushRun).where(
            RushRun.user_id == user.id, RushRun.created_at >= since))
        return (1.0, "Hecho", {}) if runs else (0.0, "Sin hacer", {})

    if kind == "daily":
        available = (daily_puzzle(db) is not None) + (own_position(db, user) is not None)
        done = db.scalar(select(func.count()).select_from(DailyChallenge).where(
            DailyChallenge.user_id == user.id, DailyChallenge.day == today(),
            DailyChallenge.kind.in_(["puzzle", "own-game"])))
        if not available:
            return 1.0, "Nada disponible hoy", {}
        return min(1.0, done / available), f"{done} de {available}", {}

    return 0.0, "", {}


def plan_for_today(db: Session, user: User) -> dict:
    coach = today_plan(db, user)  # consejos siempre al día
    plan = db.scalars(select(DailyPlan).where(DailyPlan.user_id == user.id, DailyPlan.day == today())).first()
    if plan is None:
        plan = DailyPlan(user_id=user.id, day=today(), steps=coach["steps"])
        db.add(plan)
        try:
            db.commit()
        except IntegrityError:  # dos peticiones a la vez: se usa la que ganó
            db.rollback()
            plan = db.scalars(select(DailyPlan).where(DailyPlan.user_id == user.id, DailyPlan.day == today())).first()
    steps = []
    for step in plan.steps:
        progress, label, extra = _progress(db, user, step, plan)
        out = {**step, **extra, "progress": round(progress, 2), "done": progress >= 1, "status": label}
        if step["kind"] == "review" and not step.get("game_id"):
            # «Revisa la partida de hoy» lleva directamente a la última partida jugada desde el plan
            latest = db.scalars(select(Game).where(
                Game.user_id == user.id, Game.source == "app", Game.created_at >= plan.created_at
            ).order_by(Game.created_at.desc()).limit(1)).first()
            if latest:
                out["game_id"] = latest.id
        steps.append(out)
    return {**coach, "steps": steps, "minutes": sum(s["minutes"] for s in plan.steps)}
