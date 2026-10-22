"""Sesión «Entrenar hoy»: se fija una vez al día y cada paso se completa con actividad real."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .coach import AREA_LABEL, today_plan, unreviewed_game, weak_themes
from .lessons import BY_ID, LESSONS
from .models import (
    DailyChallenge,
    DailyPlan,
    EndgameAttempt,
    Game,
    RepertoireLine,
    ReviewItem,
    RushRun,
    TrainingSession,
    User,
    WoodpeckerSet,
)
from .routers.daily import daily_puzzle, own_position
from .services import effective_split, local_midnight, seconds_by_area, today, week_start

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


def plan_for_today(db: Session, user: User, light: bool = False) -> dict:
    """`light`: solo los pasos y su progreso (para la barra de entrenamiento, que lo pide a menudo);
    sin recalcular consejos ni sugerencias, que son lo costoso."""
    plan = db.scalars(select(DailyPlan).where(DailyPlan.user_id == user.id, DailyPlan.day == today())).first()
    coach = {} if light and plan is not None else today_plan(db, user)  # consejos siempre al día
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
    return {**coach, "steps": steps, "minutes": sum(s["minutes"] for s in plan.steps),
            "extras": [] if light else suggestions(db, user)}


def _due(db: Session, user: User, kind: str) -> list[str]:
    return list(db.scalars(select(ReviewItem.ref_id).where(
        ReviewItem.user_id == user.id, ReviewItem.kind == kind, ReviewItem.due_date <= today())))


def suggestions(db: Session, user: User, limit: int = 4) -> list[dict]:
    """Actividades extra para cuando la sesión de hoy está completa, cada una con su motivo."""
    out: list[dict] = []

    # 1. Lo pendiente de repasar
    pending = unreviewed_game(db, user.id)
    if pending:
        out.append({"area": "play", "kind": "review", "game_id": pending.id, "minutes": 10,
                    "title": "Revisa tu partida pendiente", "reason": "Analizar tus propias partidas es lo que más rinde."})
    puzzles_due = _due(db, user, "puzzle")
    if puzzles_due:
        out.append({"area": "tactics", "kind": "puzzles", "review": True, "minutes": 10,
                    "title": f"Repasa {len(puzzles_due)} puzzle{'s' if len(puzzles_due) > 1 else ''} fallado{'s' if len(puzzles_due) > 1 else ''}",
                    "reason": "Toca repasarlos hoy según la repetición espaciada."})
    openings_due = _due(db, user, "opening")
    if openings_due:
        out.append({"area": "openings", "kind": "openings", "minutes": 10,
                    "title": f"Repasa {len(openings_due)} jugada{'s' if len(openings_due) > 1 else ''} de tu repertorio",
                    "reason": "Toca repasarlas hoy según la repetición espaciada."})
    endgames_due = [i for i in _due(db, user, "endgame") if i in BY_ID]
    if endgames_due:
        out.append({"area": "endgames", "kind": "endgame", "lesson_id": endgames_due[0], "minutes": 10,
                    "title": f"Final: {BY_ID[endgames_due[0]]['title']}", "reason": "Toca repasar esta posición teórica."})

    # 2. Áreas por detrás de su objetivo semanal, de más a menos retraso
    split = effective_split(user)
    week = seconds_by_area(db, user.id, week_start())
    target = {a: user.weekly_hours * 3600 * pct / 100 for a, pct in split.items()}
    behind = sorted((a for a in target if target[a] - week.get(a, 0) > 15 * 60),
                    key=lambda a: -(target[a] - week.get(a, 0)))
    weak = weak_themes(db, user.id)
    has_repertoire = db.scalar(select(func.count()).select_from(RepertoireLine).where(RepertoireLine.user_id == user.id))
    woodpecker = db.scalar(select(func.count()).select_from(WoodpeckerSet).where(
        WoodpeckerSet.user_id == user.id, WoodpeckerSet.active.is_(True)))
    won = set(db.scalars(select(EndgameAttempt.lesson_id).where(
        EndgameAttempt.user_id == user.id, EndgameAttempt.success.is_(True))))
    for area in behind:
        done_min, target_min = round(week.get(area, 0) / 60), round(target[area] / 60)
        why = f"Esta semana llevas {done_min} de {target_min} min de {AREA_LABEL[area].lower()}."
        if area == "tactics":
            if weak:
                t = weak[0]
                out.append({"area": "tactics", "kind": "puzzles", "theme": t["theme"], "minutes": 15,
                            "title": "Puzzles de tu tema más flojo",
                            "reason": f"Es tu tema más flojo ({t['accuracy']}% de acierto). {why}"})
            elif woodpecker:
                out.append({"area": "tactics", "kind": "woodpecker", "minutes": 15, "title": "Sigue tu ciclo Woodpecker", "reason": why})
            else:
                out.append({"area": "tactics", "kind": "puzzles", "minutes": 15, "title": "Más puzzles tácticos", "reason": why})
        elif area == "play" and not (pending and user.review_lock):  # bloqueada hasta revisar
            out.append({"area": "play", "kind": "game", "minutes": 30, "title": "Otra partida 15+10", "reason": why})
        elif area == "endgames":
            lesson = next((l for l in LESSONS if l["id"] not in won), None)
            if lesson:
                out.append({"area": "endgames", "kind": "endgame", "lesson_id": lesson["id"], "minutes": 15,
                            "title": f"Final: {lesson['title']}", "reason": why})
            else:
                out.append({"area": "endgames", "kind": "puzzles", "theme": "endgame", "minutes": 15,
                            "title": "Puzzles de finales", "reason": why})
        elif area == "openings":
            out.append({"area": "openings", "kind": "openings", "minutes": 10,
                        "title": "Entrena tu repertorio" if has_repertoire else "Crea tu repertorio de aperturas",
                        "reason": why})

    # 3. Siempre hay algo divertido con lo que cerrar
    best = db.scalar(select(func.max(RushRun.score)).where(RushRun.user_id == user.id, RushRun.minutes == 3))
    out.append({"area": "tactics", "kind": "rush", "minutes": 3, "title": "Contrarreloj de 3 minutos",
                "reason": f"Intenta batir tu récord de {best}." if best else "Pon a prueba tu velocidad."})

    # Sin repetir la misma actividad
    seen, unique = set(), []
    for s in out:
        key = (s["kind"], s.get("game_id"), s.get("lesson_id"), s.get("theme"), s.get("review"))
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique[:limit]
