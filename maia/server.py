"""Servicio mínimo que devuelve la jugada de Maia para una posición.

Maia se usa con un solo nodo (nodes=1): juega la jugada que más probablemente haría un humano
de ese nivel, sin búsqueda. Un proceso lc0 por nivel, arrancado bajo demanda.
"""

import threading

import chess
import chess.engine
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

LEVELS = [1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]

app = FastAPI(title="Maia")
_engines: dict[int, chess.engine.SimpleEngine] = {}
_locks = {lvl: threading.Lock() for lvl in LEVELS}


def engine_for(level: int) -> chess.engine.SimpleEngine:
    eng = _engines.get(level)
    if eng is None:
        eng = chess.engine.SimpleEngine.popen_uci(
            ["lc0", f"--weights=/weights/maia-{level}.pb.gz", "--backend=blas", "--threads=1"]
        )
        _engines[level] = eng
    return eng


class MoveIn(BaseModel):
    fen: str = Field(max_length=100)
    level: int


@app.get("/health")
def health():
    return {"ok": True, "levels": LEVELS}


@app.post("/move")
def move(body: MoveIn):
    level = min(LEVELS, key=lambda l: abs(l - body.level))
    try:
        board = chess.Board(body.fen)
    except ValueError:
        raise HTTPException(400, "FEN no válido")
    if board.is_game_over():
        raise HTTPException(400, "La partida ha terminado")
    with _locks[level]:
        try:
            result = engine_for(level).play(board, chess.engine.Limit(nodes=1))
        except chess.engine.EngineError:
            _engines.pop(level, None)  # el proceso murió: se recrea en la siguiente petición
            raise HTTPException(503, "Maia no responde")
    return {"move": result.move.uci(), "level": level}


@app.on_event("shutdown")
def shutdown():
    for eng in _engines.values():
        eng.quit()
