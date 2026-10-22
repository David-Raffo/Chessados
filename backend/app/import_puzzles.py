"""Importa puzzles de la base abierta de Lichess (CC0) a PostgreSQL.

El CSV comprimido pesa cientos de MB: se lee en streaming, se filtra por popularidad y número de
partidas, y se para al llegar a PUZZLE_LIMIT. Si existe PUZZLE_FILE (montado en /data) se usa en
lugar de descargarlo.

Ejecutar con: python -m app.import_puzzles
"""

import csv
import io
import logging
import os

import httpx
import zstandard
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from .config import PUZZLE_FILE, PUZZLE_LIMIT, PUZZLE_MIN_PLAYS, PUZZLE_MIN_POPULARITY, PUZZLE_URL
from .db import SessionLocal, engine
from .main import init_db
from .models import Puzzle

log = logging.getLogger("importer")
BATCH = 2000


def rows_from(stream) -> csv.DictReader:
    reader = zstandard.ZstdDecompressor().stream_reader(stream)
    return csv.DictReader(io.TextIOWrapper(reader, encoding="utf-8"))


def to_row(r: dict) -> dict | None:
    try:
        popularity, plays = int(r["Popularity"]), int(r["NbPlays"])
    except (KeyError, ValueError):
        return None
    if popularity < PUZZLE_MIN_POPULARITY or plays < PUZZLE_MIN_PLAYS:
        return None
    return {
        "id": r["PuzzleId"],
        "fen": r["FEN"],
        "moves": r["Moves"],
        "rating": int(r["Rating"]),
        "rating_dev": int(r["RatingDeviation"]),
        "popularity": popularity,
        "nb_plays": plays,
        "themes": r["Themes"],
        "opening_tags": r.get("OpeningTags") or None,
    }


def flush(batch: list[dict]) -> int:
    """Inserta un lote y devuelve cuántos puzzles eran nuevos (los repetidos se ignoran)."""
    with engine.begin() as conn:
        # RETURNING con ON CONFLICT DO NOTHING devuelve solo las filas insertadas
        # (rowcount no sirve: el controlador devuelve -1 en inserciones de varias filas)
        stmt = insert(Puzzle).values(batch).on_conflict_do_nothing(index_elements=["id"]).returning(Puzzle.id)
        return len(conn.execute(stmt).fetchall())


def run(reader: csv.DictReader, already: int) -> int:
    total, batch = already, []
    for r in reader:
        row = to_row(r)
        if row is None:
            continue
        batch.append(row)
        if len(batch) >= BATCH:
            total += flush(batch)
            batch = []
            log.info("%d puzzles en la base de datos", total)
            if PUZZLE_LIMIT and total >= PUZZLE_LIMIT:
                return total
    if batch:
        total += flush(batch)
    return total


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    init_db()
    with SessionLocal() as db:
        already = db.scalar(select(func.count()).select_from(Puzzle))
    if PUZZLE_LIMIT and already >= PUZZLE_LIMIT:
        log.info("ya hay %d puzzles, no se importa nada", already)
        return

    if os.path.exists(PUZZLE_FILE):
        log.info("leyendo %s", PUZZLE_FILE)
        with open(PUZZLE_FILE, "rb") as fh:
            total = run(rows_from(fh), already)
    else:
        log.info("descargando %s (se para al llegar a %s puzzles)", PUZZLE_URL, PUZZLE_LIMIT or "todos")
        with httpx.stream("GET", PUZZLE_URL, timeout=120, follow_redirects=True) as resp:
            resp.raise_for_status()
            total = run(rows_from(_IterStream(resp.iter_raw())), already)
    log.info("importación terminada: %d puzzles en la base de datos", total)


class _IterStream(io.RawIOBase):
    """Adapta un iterador de bytes a un fichero legible para zstandard."""

    def __init__(self, it):
        self._it, self._buf = it, b""

    def readable(self) -> bool:
        return True

    def readinto(self, b) -> int:
        while not self._buf:
            try:
                self._buf = next(self._it)
            except StopIteration:
                return 0
        n = min(len(b), len(self._buf))
        b[:n], self._buf = self._buf[:n], self._buf[n:]
        return n


if __name__ == "__main__":
    main()
