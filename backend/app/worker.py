"""Worker de análisis: toma partidas pendientes de la cola (PostgreSQL) y las revisa con Stockfish nativo.

Ejecutar con: python -m app.worker
"""

import io
import logging
import math
import time

import chess
import chess.engine
import chess.pgn
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .config import ANALYSIS_DEPTH, ANALYSIS_THREADS, QUICK_DEPTH, STOCKFISH_PATH
from .main import init_db
from .db import SessionLocal
from .models import Game, GameAnalysis

log = logging.getLogger("worker")

MATE_CP = 10000
PIECE_VALUES = {chess.QUEEN: 9, chess.ROOK: 5, chess.BISHOP: 3, chess.KNIGHT: 3}


def win_prob(cp: int) -> float:
    """Probabilidad de ganar (0..1) para las blancas, misma curva que Lichess."""
    return 1 / (1 + math.exp(-0.00368208 * cp))


def move_accuracy(wp_before: float, wp_after: float) -> float:
    """Precisión por jugada estilo Lichess, con probabilidades en porcentaje."""
    drop = max(0.0, (wp_before - wp_after) * 100)
    return max(0.0, min(100.0, 103.1668 * math.exp(-0.04354 * drop) - 3.1669))


def phase_of(board: chess.Board) -> str:
    material = sum(
        len(board.pieces(pt, color)) * v for pt, v in PIECE_VALUES.items() for color in chess.COLORS
    )
    if material <= 26:
        return "endgame"
    if board.fullmove_number <= 12:
        return "opening"
    return "middlegame"


def classify(drop: float, is_best: bool) -> str:
    # Umbrales de Lichess (0.1/0.2/0.3 en escala -1..1 → 0.05/0.10/0.15 en probabilidad)
    if is_best:
        return "best"
    if drop >= 0.15:
        return "blunder"
    if drop >= 0.10:
        return "mistake"
    if drop >= 0.05:
        return "inaccuracy"
    return "good"


def error_type(board_after: chess.Board, reply: chess.Move | None, phase: str) -> str:
    if phase == "endgame":
        return "mal final"
    if reply is not None and board_after.is_capture(reply):
        captured = board_after.piece_at(reply.to_square)
        if captured and captured.piece_type != chess.PAWN:
            return "pieza colgada"
    return "amenaza no vista"


def score_cp(info: chess.engine.InfoDict) -> tuple[int, int | None]:
    score = info["score"].white()
    return max(-MATE_CP, min(MATE_CP, score.score(mate_score=MATE_CP))), score.mate()


def analyse_game(engine: chess.engine.SimpleEngine, game: Game, depth: int) -> tuple[list[GameAnalysis], float | None]:
    parsed = chess.pgn.read_game(io.StringIO(game.pgn))
    if parsed is None:
        raise ValueError("PGN no válido")
    board = parsed.board()
    moves = list(parsed.mainline_moves())
    user_white = game.user_color == "white"

    # Una evaluación por posición (n jugadas → n + 1 posiciones)
    infos = []
    b = board.copy()
    for i in range(len(moves) + 1):
        if b.is_game_over():
            outcome = b.outcome()
            cp = 0 if outcome.winner is None else (MATE_CP if outcome.winner else -MATE_CP)
            infos.append({"cp": cp, "mate": None, "pv": []})
        else:
            info = engine.analyse(b, chess.engine.Limit(depth=depth))
            cp, mate = score_cp(info)
            infos.append({"cp": cp, "mate": mate, "pv": info.get("pv", [])})
        if i < len(moves):
            b.push(moves[i])

    rows: list[GameAnalysis] = []
    accs: list[float] = []
    b = board.copy()
    for i, move in enumerate(moves):
        before, after = infos[i], infos[i + 1]
        mover_white = b.turn == chess.WHITE
        fen_before = b.fen()
        san = b.san(move)
        best = before["pv"][0] if before["pv"] else None
        best_san = b.san(best) if best else None
        pv_board = b.copy()
        pv_san = []
        for m in before["pv"][:8]:
            pv_san.append(pv_board.san(m))
            pv_board.push(m)

        wp_before = win_prob(before["cp"]) if mover_white else 1 - win_prob(before["cp"])
        wp_after = win_prob(after["cp"]) if mover_white else 1 - win_prob(after["cp"])
        drop = max(0.0, wp_before - wp_after)
        cls = classify(drop, best == move)
        phase = phase_of(b)

        b.push(move)
        is_user = mover_white == user_white
        etype = None
        if is_user and cls in ("mistake", "blunder"):
            reply = after["pv"][0] if after["pv"] else None
            etype = error_type(b, reply, phase)
        if is_user:
            accs.append(move_accuracy(wp_before, wp_after))

        rows.append(GameAnalysis(
            ply=i + 1, san=san, uci=move.uci(), fen_before=fen_before, eval_cp=after["cp"], mate=after["mate"],
            best_uci=best.uci() if best else None, best_san=best_san, pv_san=" ".join(pv_san),
            classification=cls, phase=phase, error_type=etype, is_user_move=is_user,
        ))
    accuracy = round(sum(accs) / len(accs), 1) if accs else None
    return rows, accuracy


# Estados: pending → (pasada rápida) running → quick → (pasada profunda) refining → done.
# La pasada rápida se ve en segundos; la profunda afina el resultado en segundo plano.
# Las pasadas rápidas de partidas nuevas tienen prioridad sobre las profundas.


def claim_next() -> tuple[int, str] | None:
    with SessionLocal() as db:
        for status, claimed, kind in (("pending", "running", "quick"), ("quick", "refining", "deep")):
            game = db.scalars(
                select(Game)
                .where(Game.analysis_status == status)
                .order_by(Game.created_at.desc())  # primero lo recién jugado
                .limit(1)
                .with_for_update(skip_locked=True)
            ).first()
            if game is not None:
                game.analysis_status = claimed
                db.commit()
                return game.id, kind
    return None


class EngineDied(Exception):
    """Stockfish se ha caído: hay que arrancar otro y repetir la partida."""


def process(engine: chess.engine.SimpleEngine, game_id: int, kind: str) -> None:
    depth = QUICK_DEPTH if kind == "quick" else ANALYSIS_DEPTH
    with SessionLocal() as db:
        game = db.get(Game, game_id)
        if game is None:  # borrada mientras esperaba
            return
        try:
            start = time.time()
            rows, accuracy = analyse_game(engine, game, depth)
            game.analysis.clear()
            game.analysis.extend(rows)
            game.accuracy = accuracy
            game.analysis_depth = depth
            game.analysis_status = "quick" if kind == "quick" else "done"
            log.info("partida %s: pasada %s (prof. %d, %d jugadas, %.1fs)",
                     game_id, kind, depth, len(rows), time.time() - start)
        except (chess.engine.EngineTerminatedError, chess.engine.EngineError) as e:
            # No es culpa de la partida: vuelve a la cola y se analiza con un Stockfish nuevo
            game.analysis_status = "pending" if kind == "quick" else "quick"
            _safe_commit(db, game_id)
            raise EngineDied() from e
        except Exception:
            log.exception("error analizando la partida %s", game_id)
            # Si falla la profunda, se queda con la rápida
            game.analysis_status = "done" if kind == "deep" and game.analysis else "error"
        _safe_commit(db, game_id)


def _safe_commit(db, game_id: int) -> None:
    """Si la partida se borró mientras se analizaba, se descarta el resultado sin tumbar el worker."""
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        log.warning("la partida %s ya no existe; se descarta su análisis", game_id)


def start_engine() -> chess.engine.SimpleEngine:
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    engine.configure({"Threads": ANALYSIS_THREADS, "Hash": 128})
    log.info("Stockfish listo: %s, profundidad %d", engine.id.get("name"), ANALYSIS_DEPTH)
    return engine


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    init_db()
    with SessionLocal() as db:
        # Si el worker murió a mitad de un análisis, se reintenta
        for g in db.scalars(select(Game).where(Game.analysis_status.in_(["running", "refining"]))):
            g.analysis_status = "pending" if g.analysis_status == "running" else "quick"
        db.commit()

    engine = start_engine()
    try:
        while True:
            try:
                job = claim_next()
                if job is None:
                    time.sleep(1)
                    continue
                process(engine, *job)
            except EngineDied:
                log.warning("Stockfish se ha caído; arranco uno nuevo")
                try:
                    engine.quit()
                except Exception:
                    pass
                time.sleep(1)
                engine = start_engine()
            except Exception:
                # Un fallo puntual (p. ej. la base de datos reiniciándose) no debe parar el worker
                log.exception("error en el bucle del worker")
                time.sleep(5)
    finally:
        engine.quit()


if __name__ == "__main__":
    main()
