"""Nombres de aperturas (lichess-org/chess-openings, CC0) y utilidades del repertorio."""

import csv
import io
from functools import lru_cache
from pathlib import Path

import chess
import chess.pgn

DATA = Path(__file__).parent / "data" / "openings"


def epd(board: chess.Board) -> str:
    """Clave de posición sin contadores de jugadas (transposiciones incluidas)."""
    return board.epd()


@lru_cache(maxsize=1)
def names() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for path in sorted(DATA.glob("*.tsv")):
        with path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                game = chess.pgn.read_game(io.StringIO(row["pgn"]))
                if game is None:
                    continue
                board = game.end().board()
                out[epd(board)] = (row["eco"], row["name"])
    return out


def name_for_moves(moves: list[chess.Move], start: chess.Board | None = None) -> dict | None:
    """Nombre más profundo que coincide con la secuencia de jugadas."""
    board = start.copy() if start else chess.Board()
    table = names()
    best = table.get(epd(board))
    for m in moves:
        board.push(m)
        hit = table.get(epd(board))
        if hit:
            best = hit
    return {"eco": best[0], "name": best[1]} if best else None


# Repertorios de ejemplo para no empezar en blanco (secuencias UCI)
STARTERS = {
    "white": [
        "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 d2d3",
        "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3",
        "e2e4 e7e5 g1f3 d7d6 d2d4",
        "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4",
        "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4",
        "e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4",
        "e2e4 e7e6 d2d4 d7d5 e4e5 c7c5 c2c3",
        "e2e4 c7c6 d2d4 d7d5 e4e5 c8f5 g1f3",
        "e2e4 d7d5 e4d5 d8d5 b1c3 d5a5 d2d4",
    ],
    "black": [
        "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 b5a4 g8f6",
        "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5",
        "e2e4 e7e5 g1f3 b8c6 d2d4 e5d4 f3d4 g8f6",
        "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6",
        "d2d4 d7d5 g1f3 g8f6 c2c4 e7e6",
        "c2c4 e7e5",
        "g1f3 d7d5",
    ],
}
