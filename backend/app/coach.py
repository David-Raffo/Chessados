"""Entrenador por reglas simples y transparentes (sin IA externa)."""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .lessons import LESSONS
from .models import (
    DailyChallenge,
    EndgameAttempt,
    Game,
    GameAnalysis,
    Puzzle,
    PuzzleAttempt,
    Rating,
    RepertoireLine,
    ReviewItem,
    User,
    WoodpeckerSet,
)
from .services import effective_split, local_midnight, seconds_by_area, today, week_start

AREA_LABEL = {
    "tactics": "Táctica",
    "play": "Partidas",
    "endgames": "Finales",
    "openings": "Aperturas",
    "rush": "Contrarreloj",
}


def theme_stats(db: Session, user_id: int, days: int = 30) -> list[dict]:
    """Precisión y tiempo medio por tema táctico en los últimos `days` días."""
    since = local_midnight(today() - timedelta(days=days))
    rows = db.execute(
        select(Puzzle.themes, PuzzleAttempt.solved, PuzzleAttempt.seconds)
        .join(Puzzle, Puzzle.id == PuzzleAttempt.puzzle_id)
        .where(PuzzleAttempt.user_id == user_id, PuzzleAttempt.created_at >= since)
    ).all()
    agg: dict[str, list] = {}
    for themes, solved, secs in rows:
        for t in themes.split():
            a = agg.setdefault(t, [0, 0, 0.0])
            a[0] += 1
            a[1] += int(solved)
            a[2] += secs
    out = [
        {"theme": t, "attempts": n, "accuracy": round(100 * ok / n), "avg_seconds": round(s / n, 1)}
        for t, (n, ok, s) in agg.items()
    ]
    return sorted(out, key=lambda x: -x["attempts"])


IGNORED_THEMES = {"short", "long", "veryLong", "oneMove", "middlegame", "opening", "endgame", "master",
                  "masterVsMaster", "superGM", "crushing", "advantage", "equality", "mate"}


WEAK_MIN_ATTEMPTS = 5
WEAK_PRIOR = 6  # intentos «imaginarios» con tu acierto medio: frena conclusiones con pocos datos


def weak_themes(db: Session, user_id: int) -> list[dict]:
    """Temas en los que aciertas claramente menos que en el resto.

    Se ordenan por un acierto suavizado hacia tu media: con pocos intentos pesa la media, con muchos
    tu acierto real. Así un tema muy practicado (y por eso con muchos datos) no queda siempre el último
    solo porque los demás no llegan al mínimo, y uno con 3 de 6 cuenta como más flojo que 26 de 37.
    """
    rows = [t for t in theme_stats(db, user_id) if t["theme"] not in IGNORED_THEMES]
    n_all = sum(t["attempts"] for t in rows)
    ok_all = sum(t["attempts"] * t["accuracy"] / 100 for t in rows)
    if not n_all:
        return []
    mean = ok_all / n_all
    out = []
    for t in rows:
        if t["attempts"] < WEAK_MIN_ATTEMPTS:
            continue
        smoothed = (t["attempts"] * t["accuracy"] / 100 + WEAK_PRIOR * mean) / (t["attempts"] + WEAK_PRIOR)
        if smoothed < mean - 0.03:  # solo si de verdad estás por debajo de tu media
            out.append({**t, "score": round(100 * smoothed)})
    return sorted(out, key=lambda x: x["score"])[:3]


# Temas tácticos que se pueden entrenar con filtro (como THEME_FILTERS del frontend, sin los de finales)
TRAINABLE_THEMES = [
    "fork", "pin", "skewer", "discoveredAttack", "hangingPiece", "sacrifice", "deflection", "attraction",
    "mateIn1", "mateIn2", "mateIn3", "backRankMate", "promotion", "trappedPiece", "intermezzo", "quietMove",
]
FRESH_MAX_ATTEMPTS = 3  # con menos intentos que esto, el tema cuenta como «sin practicar»


def fresh_themes(db: Session, user_id: int) -> list[str]:
    """Temas entrenables que casi no has practicado nunca, de menos a más intentos.

    A igualdad de intentos el orden cambia cada día, para no proponer siempre el mismo.
    """
    counts = {t["theme"]: t["attempts"] for t in theme_stats(db, user_id, days=3650)}
    day = today().toordinal()
    fresh = [t for t in TRAINABLE_THEMES if counts.get(t, 0) < FRESH_MAX_ATTEMPTS]
    return sorted(fresh, key=lambda t: (counts.get(t, 0), (TRAINABLE_THEMES.index(t) + day) % len(TRAINABLE_THEMES)))


def blunder_phases(db: Session, user_id: int, days: int = 30, not_before: date | None = None) -> dict[str, int]:
    """Errores graves por fase en partidas jugadas en los últimos `days` días (y no antes de `not_before`)."""
    start = today() - timedelta(days=days)
    if not_before and not_before > start:
        start = not_before
    since = local_midnight(start)
    rows = db.execute(
        select(GameAnalysis.phase, func.count())
        .join(Game, Game.id == GameAnalysis.game_id)
        .where(
            Game.user_id == user_id,
            Game.played_at >= since,  # fecha de la partida, no de la importación
            GameAnalysis.is_user_move.is_(True),
            GameAnalysis.classification == "blunder",
        )
        .group_by(GameAnalysis.phase)
    ).all()
    return {p: n for p, n in rows}


def unreviewed_game(db: Session, user_id: int) -> Game | None:
    return db.scalars(
        select(Game)
        .where(Game.user_id == user_id, Game.source == "app", Game.reviewed.is_(False))
        .order_by(Game.created_at.desc())
        .limit(1)
    ).first()


def stagnant_areas(db: Session, user_id: int) -> list[str]:
    """Áreas con actividad cuyo rating no ha subido en 4 semanas."""
    cutoff = local_midnight(today() - timedelta(days=28))
    out = []
    for area in ("tactics", "play", "rush"):
        first = db.execute(
            select(func.min(Rating.created_at)).where(Rating.user_id == user_id, Rating.area == area)
        ).scalar()
        if first is None or first > cutoff:
            continue
        old = db.scalars(
            select(Rating.rating)
            .where(Rating.user_id == user_id, Rating.area == area, Rating.created_at <= cutoff)
            .order_by(Rating.created_at.desc())
            .limit(1)
        ).first()
        new = db.scalars(
            select(Rating.rating)
            .where(Rating.user_id == user_id, Rating.area == area)
            .order_by(Rating.created_at.desc())
            .limit(1)
        ).first()
        recent = db.execute(
            select(func.count()).select_from(Rating).where(
                Rating.user_id == user_id, Rating.area == area, Rating.created_at > cutoff
            )
        ).scalar()
        if old is not None and new is not None and recent >= 10 and new <= old:
            out.append(area)
    return out


def today_plan(db: Session, user: User) -> dict:
    split = effective_split(user)
    week = seconds_by_area(db, user.id, week_start())
    total = sum(week.values())
    deficits = {}
    for area, target in split.items():
        share = 100 * week.get(area, 0) / total if total else 0
        deficits[area] = target - share

    advice: list[dict] = []
    minutes = max(30, min(120, round(user.weekly_hours * 60 / 7 / 5) * 5))

    # Regla 3: demasiados errores graves en el final. Tras un refuerzo de dos semanas solo cuentan
    # los errores de partidas posteriores a su inicio; si no, los mismos errores lo reactivarían siempre.
    boost_start = user.endgame_boost_until - timedelta(days=14) if user.endgame_boost_until else None
    phases = blunder_phases(db, user.id, not_before=boost_start)
    n_blunders = sum(phases.values())
    if n_blunders >= 5 and phases.get("endgame", 0) / n_blunders > 0.3:
        if not user.endgame_boost_until or user.endgame_boost_until < today():
            user.endgame_boost_until = today() + timedelta(days=14)
            db.commit()
            split = effective_split(user)
        pct = round(100 * phases["endgame"] / n_blunders)
        advice.append({
            "rule": 3, "area": "endgames",
            "text": f"El {pct}% de tus errores graves llegan en el final. Subo los finales al 25% durante dos semanas.",
        })

    # Regla 2: temas tácticos por debajo del 60%
    weak = [t for t in weak_themes(db, user.id) if t["accuracy"] < 60]
    for t in weak[:2]:
        advice.append({
            "rule": 2, "area": "tactics", "theme": t["theme"],
            "text": f"Aciertas solo el {t['accuracy']}% en «{t['theme']}». Te preparo un bloque de 20 puzzles de ese tema.",
        })

    # Regla 4: partidas sin revisar
    pending = unreviewed_game(db, user.id)
    if pending:
        lock = " La siguiente partida queda bloqueada hasta que la revises." if user.review_lock else ""
        advice.append({
            "rule": 4, "area": "play", "game_id": pending.id,
            "text": f"Tienes una partida sin revisar.{lock}",
        })

    # Regla 5: estancamiento
    for area in stagnant_areas(db, user.id):
        tip = {
            "tactics": "Prueba el modo Woodpecker: el mismo bloque de puzzles en ciclos cada vez más rápidos.",
            "play": "Cambia de ritmo: juega 30+0 o contra Maia, y revisa cada partida antes de mirar el motor.",
            "rush": "Haz puzzles normales sin reloj durante una semana: primero precisión, luego velocidad.",
        }[area]
        advice.append({"rule": 5, "area": area, "text": f"Tu ELO de {AREA_LABEL[area]} no sube en 4 semanas. {tip}",
                       "link": "/woodpecker" if area == "tactics" else None})

    # Estado de los módulos de finales, aperturas, Woodpecker y desafíos
    endgame_due = db.scalars(select(ReviewItem.ref_id).where(
        ReviewItem.user_id == user.id, ReviewItem.kind == "endgame", ReviewItem.due_date <= today())).all()
    tried = set(db.scalars(select(EndgameAttempt.lesson_id).where(
        EndgameAttempt.user_id == user.id, EndgameAttempt.success.is_(True))))
    next_lesson = next((l for l in LESSONS if l["id"] not in tried), None)
    opening_due = db.scalar(select(func.count()).select_from(ReviewItem).where(
        ReviewItem.user_id == user.id, ReviewItem.kind == "opening", ReviewItem.due_date <= today()))
    has_repertoire = db.scalar(select(func.count()).select_from(RepertoireLine).where(
        RepertoireLine.user_id == user.id))
    woodpecker = db.scalar(select(func.count()).select_from(WoodpeckerSet).where(
        WoodpeckerSet.user_id == user.id, WoodpeckerSet.active.is_(True)))
    daily_done = db.scalar(select(func.count()).select_from(DailyChallenge).where(
        DailyChallenge.user_id == user.id, DailyChallenge.day == today()))

    if not has_repertoire:
        advice.append({"rule": 0, "area": "openings", "link": "/aperturas",
                       "text": "Aún no tienes repertorio. Crea uno (o carga el de ejemplo) para entrenar tus aperturas con repetición espaciada."})

    # Regla 1: área más de 10 puntos por debajo de su objetivo
    available = ["tactics", "play", "endgames"] + (["openings"] if has_repertoire else [])
    behind = sorted(
        (a for a in available if deficits.get(a, 0) > 10), key=lambda a: -deficits[a]
    )
    if behind and total:
        a = behind[0]
        advice.insert(0, {
            "rule": 1, "area": a,
            "text": f"{AREA_LABEL[a]} va {round(deficits[a])} puntos por debajo de su objetivo semanal: hoy empezamos por ahí.",
        })

    fresh = fresh_themes(db, user.id)

    # Construcción de la sesión de hoy
    if endgame_due:
        endgame_block = {"area": "endgames", "kind": "endgame", "minutes": round(minutes * 0.2),
                         "title": f"Repasa {len(endgame_due)} final{'es' if len(endgame_due) > 1 else ''} teórico{'s' if len(endgame_due) > 1 else ''}",
                         "lesson_id": endgame_due[0]}
    elif next_lesson:
        endgame_block = {"area": "endgames", "kind": "endgame", "minutes": round(minutes * 0.2),
                         "title": f"Final: {next_lesson['title']}", "lesson_id": next_lesson["id"]}
    else:
        endgame_block = {"area": "endgames", "kind": "puzzles", "minutes": round(minutes * 0.2),
                         "title": "Puzzles de finales", "theme": "endgame"}
    blocks: dict[str, dict] = {
        "tactics": (
            {"area": "tactics", "kind": "woodpecker", "minutes": round(minutes * 0.4), "title": "Ciclo Woodpecker"}
            if woodpecker else
            {"area": "tactics", "kind": "puzzles", "minutes": round(minutes * 0.4),
             # Primero lo que aún no has probado; si ya has tocado todo, tu tema más flojo
             "title": "Puzzles tácticos", "theme": fresh[0] if fresh else (weak[0]["theme"] if weak else None)}
        ),
        # Jugar y revisar es una sola tarea: revisar sin haber jugado no tiene sentido
        "play": {"area": "play", "kind": "game", "minutes": 40, "title": "Juega una partida 15+10 y revísala",
                 "with_review": True},
        "endgames": endgame_block,
        "openings": {"area": "openings", "kind": "openings", "minutes": 10,
                     "title": f"Repaso del repertorio ({opening_due} pendientes)" if opening_due else "Amplía tu repertorio"},
    }
    order = behind + [a for a in sorted(available, key=lambda a: -split.get(a, 0)) if a not in behind]
    candidates = []
    if not daily_done and daily_available(db, user):
        candidates.append({"area": "tactics", "kind": "daily", "minutes": 5, "title": "Desafíos del día"})
    if pending:
        candidates.append({"area": "play", "kind": "review", "minutes": 10, "title": "Revisa tu última partida",
                           "game_id": pending.id})
    for a in order:
        candidates.append(blocks[a])
    candidates.append({"area": "tactics", "kind": "rush", "minutes": 5, "title": "Contrarreloj de 5 minutos"})

    # Se llenan los minutos del día en orden de prioridad; siempre al menos dos bloques
    steps, used = [], 0
    for step in candidates:
        if len(steps) < 3 or used + step["minutes"] <= minutes:
            steps.append(step)
            used += step["minutes"]

    if not advice:
        advice.append({"rule": 0, "area": "tactics",
                       "text": "Vas bien. Mantén la rutina: la constancia rinde más que un plan perfecto."})

    return {"minutes": minutes, "split": split, "steps": steps, "advice": advice,
            "weak_themes": weak_themes(db, user.id)}


def daily_available(db: Session, user: User) -> bool:
    from .routers.daily import daily_puzzle, own_position  # import diferido: evita ciclo con routers

    return daily_puzzle(db) is not None or own_position(db, user) is not None


def review_locked(db: Session, user: User) -> Game | None:
    if not user.review_lock:
        return None
    return unreviewed_game(db, user.id)
