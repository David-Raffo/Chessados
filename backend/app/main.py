import time

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .db import Base, engine
from .routers import daily, endgames, games, maia, openings, puzzles, sessions, stats, users, woodpecker


def init_db(retries: int = 30) -> None:
    """Crea las tablas; espera a que PostgreSQL acepte conexiones al arrancar con compose."""
    for attempt in range(retries):
        try:
            # api, worker e importador arrancan a la vez: el lock evita crear las tablas dos veces
            with engine.begin() as conn:
                conn.execute(text("SELECT pg_advisory_xact_lock(4242)"))
                Base.metadata.create_all(conn)
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


for module in (users, sessions, puzzles, games, stats, maia, endgames, openings, woodpecker, daily):
    app.include_router(module.router)
