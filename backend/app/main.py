import time

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .db import Base, engine
from .learn import OLD_ENDGAMES
from .routers import daily, endgames, games, learn, maia, openings, puzzles, sessions, stats, users, woodpecker


def migrate(conn) -> None:
    """Cambios de esquema sobre bases de datos ya creadas (create_all no modifica tablas)."""
    columns = {
        row[0]
        for row in conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"
        ))
    }
    if "email" in columns and "username" not in columns:
        # Las cuentas pasan de email a nombre de usuario: la parte antes de la @ hace de usuario
        conn.execute(text("ALTER TABLE users RENAME COLUMN email TO username"))
        conn.execute(text("UPDATE users SET username = left(lower(split_part(username, '@', 1)), 24) || '_' || id"))
        conn.execute(text("ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(30)"))
        conn.execute(text("ALTER INDEX IF EXISTS ix_users_email RENAME TO ix_users_username"))
    # Búsqueda de puzzles por tema: índice sobre la lista de temas (rápido aunque haya millones)
    conn.execute(text(
        "DO $$ BEGIN IF to_regclass('puzzles') IS NOT NULL THEN "
        "CREATE INDEX IF NOT EXISTS ix_puzzles_themes ON puzzles USING gin (string_to_array(themes, ' ')); "
        "END IF; END $$"
    ))
    # Análisis en dos pasadas: profundidad de la última pasada guardada
    conn.execute(text("ALTER TABLE IF EXISTS games ADD COLUMN IF NOT EXISTS analysis_depth INTEGER"))
    if columns and "is_admin" not in columns:
        # Invitaciones: la cuenta más antigua pasa a ser la de administrador
        conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT false"))
        conn.execute(text("ALTER TABLE users ADD COLUMN invited_by INTEGER REFERENCES users(id) ON DELETE SET NULL"))
        conn.execute(text("UPDATE users SET is_admin = true WHERE id = (SELECT min(id) FROM users)"))


def migrate_old_endgames(conn) -> None:
    """Cada final ganado en la antigua pantalla «Finales» queda como lección hecha en Aprender."""
    values = ", ".join(f"('{old}', '{new}')" for old, new in OLD_ENDGAMES.items())
    conn.execute(text(
        "INSERT INTO lesson_progress (user_id, lesson_id, step, completed_at) "
        f"SELECT a.user_id, m.new, 0, min(a.created_at) FROM endgame_attempts a JOIN (VALUES {values}) AS m(old, new) "
        "ON m.old = a.lesson_id WHERE a.success GROUP BY a.user_id, m.new "
        "ON CONFLICT (user_id, lesson_id) DO UPDATE SET completed_at = "
        "COALESCE(lesson_progress.completed_at, EXCLUDED.completed_at)"
    ))


def init_db(retries: int = 30) -> None:
    """Crea las tablas; espera a que PostgreSQL acepte conexiones al arrancar con compose."""
    for attempt in range(retries):
        try:
            # api, worker e importador arrancan a la vez: el lock evita crear las tablas dos veces
            with engine.begin() as conn:
                conn.execute(text("SELECT pg_advisory_xact_lock(4242)"))
                migrate(conn)
                Base.metadata.create_all(conn)
                migrate_old_endgames(conn)
            return
        except OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(2)


app = FastAPI(title="Chessados – entrenador de ajedrez", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True}


for module in (users, sessions, puzzles, games, stats, maia, endgames, openings, woodpecker, daily, learn):
    app.include_router(module.router)
