import io
from collections import deque
from datetime import timedelta

import chess
import chess.pgn
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import String, cast, func, select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..db import get_db
from ..models import Game, RepertoireLine, ReviewItem, User
from ..openings import STARTERS, epd, name_for_moves
from ..services import today

router = APIRouter(prefix="/api/openings", tags=["aperturas"])

START = epd(chess.Board())


def _lines(db: Session, user: User, color: str) -> list[RepertoireLine]:
    return list(db.scalars(select(RepertoireLine).where(RepertoireLine.user_id == user.id, RepertoireLine.color == color)))


def _user_turn(fen_key: str, color: str) -> bool:
    return fen_key.split(" ")[1] == ("w" if color == "white" else "b")


def _graph(lines: list[RepertoireLine]) -> dict[str, list[RepertoireLine]]:
    g: dict[str, list[RepertoireLine]] = {}
    for line in lines:
        g.setdefault(line.fen, []).append(line)
    return g


def _child(fen_key: str, uci: str) -> str:
    b = chess.Board(fen_key)
    b.push(chess.Move.from_uci(uci))
    return epd(b)


def _path_to(lines: list[RepertoireLine], target: str) -> list[str] | None:
    """Jugadas (UCI) desde la posición inicial hasta `target` siguiendo el repertorio."""
    g = _graph(lines)
    prev: dict[str, tuple[str, str] | None] = {START: None}
    queue = deque([START])
    while queue:
        cur = queue.popleft()
        if cur == target:
            path = []
            while prev[cur] is not None:
                parent, uci = prev[cur]
                path.append(uci)
                cur = parent
            return list(reversed(path))
        for line in g.get(cur, []):
            nxt = _child(cur, line.move)
            if nxt not in prev:
                prev[nxt] = (cur, line.move)
                queue.append(nxt)
    return None


def line_out(line: RepertoireLine) -> dict:
    board = chess.Board(line.fen)
    move = chess.Move.from_uci(line.move)
    return {"id": line.id, "fen": line.fen, "move": line.move, "san": board.san(move), "comment": line.comment}


def _ensure_review(db: Session, user: User, line: RepertoireLine) -> None:
    if not _user_turn(line.fen, line.color):
        return
    exists_ = db.scalar(select(func.count()).select_from(ReviewItem).where(
        ReviewItem.user_id == user.id, ReviewItem.kind == "opening", ReviewItem.ref_id == str(line.id)))
    if not exists_:
        db.add(ReviewItem(user_id=user.id, kind="opening", ref_id=str(line.id), due_date=today(), interval=0, reps=0))


def _delete_subtree(db: Session, user: User, color: str, line: RepertoireLine) -> int:
    """Borra una jugada y todo lo que cuelga de ella (si no se llega por otra transposición)."""
    lines = _lines(db, user, color)
    remaining = [l for l in lines if l.id != line.id]
    reachable = set()
    g = _graph(remaining)
    queue = deque([START])
    while queue:
        cur = queue.popleft()
        if cur in reachable:
            continue
        reachable.add(cur)
        for l in g.get(cur, []):
            queue.append(_child(cur, l.move))
    removed = [line] + [l for l in remaining if l.fen not in reachable]
    ids = [str(l.id) for l in removed]
    for item in db.scalars(select(ReviewItem).where(
            ReviewItem.user_id == user.id, ReviewItem.kind == "opening", ReviewItem.ref_id.in_(ids))):
        db.delete(item)
    for l in removed:
        db.delete(l)
    return len(removed)


@router.get("/repertoire")
def repertoire(color: str = "white", user: User = Depends(current_user), db: Session = Depends(get_db)):
    lines = _lines(db, user, color)
    due = db.scalar(select(func.count()).select_from(ReviewItem).join(
        RepertoireLine, ReviewItem.ref_id == cast(RepertoireLine.id, String)
    ).where(ReviewItem.user_id == user.id, ReviewItem.kind == "opening", ReviewItem.due_date <= today(),
            RepertoireLine.color == color))
    return {"lines": [line_out(l) for l in lines], "due": due}


class AddIn(BaseModel):
    color: str = Field(pattern="^(white|black)$")
    fen: str = Field(max_length=100)
    move: str = Field(pattern="^[a-h][1-8][a-h][1-8][qrbn]?$")
    comment: str | None = Field(default=None, max_length=500)


@router.post("/repertoire")
def add_line(body: AddIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        board = chess.Board(body.fen)
    except ValueError:
        raise HTTPException(400, "FEN no válido")
    move = chess.Move.from_uci(body.move)
    if move not in board.legal_moves:
        raise HTTPException(400, "Jugada ilegal")
    key = epd(board)
    lines = [l for l in _lines(db, user, body.color) if l.fen == key]
    if any(l.move == body.move for l in lines):
        line = next(l for l in lines if l.move == body.move)
        if body.comment is not None:
            line.comment = body.comment
        db.commit()
        return line_out(line)
    replaced = 0
    if _user_turn(key, body.color):
        # En tus posiciones el repertorio tiene una sola respuesta: la nueva sustituye a la anterior
        for old in lines:
            replaced += _delete_subtree(db, user, body.color, old)
        db.flush()
    line = RepertoireLine(user_id=user.id, color=body.color, fen=key, move=body.move, comment=body.comment)
    db.add(line)
    db.flush()
    _ensure_review(db, user, line)
    db.commit()
    return {**line_out(line), "replaced": replaced}


@router.delete("/repertoire/{line_id}")
def delete_line(line_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    line = db.get(RepertoireLine, line_id)
    if not line or line.user_id != user.id:
        raise HTTPException(404, "Línea no encontrada")
    n = _delete_subtree(db, user, line.color, line)
    db.commit()
    return {"deleted": n}


@router.post("/starter/{color}")
def load_starter(color: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if color not in STARTERS:
        raise HTTPException(404, "Color no válido")
    existing = {(l.fen, l.move) for l in _lines(db, user, color)}
    added = 0
    for seq in STARTERS[color]:
        board = chess.Board()
        for uci in seq.split():
            move = chess.Move.from_uci(uci)
            if move not in board.legal_moves:
                break
            key = epd(board)
            if (key, uci) not in existing:
                # No pisa una respuesta propia ya elegida por el usuario
                if _user_turn(key, color) and any(f == key for f, _ in existing):
                    break
                line = RepertoireLine(user_id=user.id, color=color, fen=key, move=uci)
                db.add(line)
                db.flush()
                _ensure_review(db, user, line)
                existing.add((key, uci))
                added += 1
            board.push(move)
    db.commit()
    return {"added": added}


class NameIn(BaseModel):
    moves: list[str] = Field(max_length=300)


@router.post("/name")
def opening_name(body: NameIn, _: User = Depends(current_user)):
    board = chess.Board()
    moves = []
    for uci in body.moves:
        try:
            m = chess.Move.from_uci(uci)
        except ValueError:
            break
        if m not in board.legal_moves:
            break
        board.push(m)
        moves.append(m)
    return name_for_moves(moves) or {"eco": None, "name": None}


# --- Entrenamiento con repetición espaciada (SM-2) ---------------------------


@router.get("/train")
def train_next(color: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = (
        select(ReviewItem, RepertoireLine)
        .join(RepertoireLine, ReviewItem.ref_id == cast(RepertoireLine.id, String))
        .where(ReviewItem.user_id == user.id, ReviewItem.kind == "opening", ReviewItem.due_date <= today())
        .order_by(ReviewItem.due_date, func.random())
    )
    if color:
        q = q.where(RepertoireLine.color == color)
    for item, line in db.execute(q.limit(20)).all():
        path = _path_to(_lines(db, user, line.color), line.fen)
        if path is None:
            continue  # posición huérfana (no se llega desde el inicio)
        return {"line_id": line.id, "color": line.color, "path": path, "move": line.move,
                "san": line_out(line)["san"], "comment": line.comment, "reps": item.reps}
    return None  # nada pendiente hoy


class TrainIn(BaseModel):
    correct: bool


@router.post("/train/{line_id}")
def train_answer(line_id: int, body: TrainIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.scalars(select(ReviewItem).where(
        ReviewItem.user_id == user.id, ReviewItem.kind == "opening", ReviewItem.ref_id == str(line_id))).first()
    if not item:
        raise HTTPException(404, "Línea no encontrada")
    if body.correct:
        item.reps += 1
        item.interval = 1 if item.reps == 1 else 3 if item.reps == 2 else round(max(item.interval, 1) * item.ease)
        item.ease = min(3.0, item.ease + 0.1)
    else:
        item.reps = 0
        item.interval = 1
        item.ease = max(1.3, item.ease - 0.2)
    item.due_date = today() + timedelta(days=item.interval)
    db.commit()
    return {"interval": item.interval, "due": item.due_date.isoformat()}


# --- Desviaciones del repertorio en tus partidas -----------------------------


def game_deviation(game: Game, lines: list[RepertoireLine]) -> dict | None:
    g = _graph(lines)
    parsed = chess.pgn.read_game(io.StringIO(game.pgn))
    if parsed is None or parsed.board().fen() != chess.STARTING_FEN:
        return None
    board = parsed.board()
    moves = list(parsed.mainline_moves())
    for ply, move in enumerate(moves, start=1):
        key = epd(board)
        options = g.get(key)
        if not options:
            return None if ply == 1 else {"ply": ply - 1, "type": "end", "san": None, "expected": None}
        mine = _user_turn(key, game.user_color)
        if all(o.move != move.uci() for o in options):
            expected = [board.san(chess.Move.from_uci(o.move)) for o in options]
            return {
                "ply": ply,
                "type": "you" if mine else "opponent",
                "san": board.san(move),
                "expected": expected,
                "fen": board.fen(),
                "path": [m.uci() for m in moves[: ply - 1]],
            }
        board.push(move)
    return None


@router.get("/deviations")
def deviations(game_id: int | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = select(Game).where(Game.user_id == user.id).order_by(Game.played_at.desc())
    q = q.where(Game.id == game_id) if game_id else q.limit(30)
    reps = {c: _lines(db, user, c) for c in ("white", "black")}
    out = []
    for game in db.scalars(q):
        lines = reps[game.user_color]
        dev = game_deviation(game, lines) if lines else None
        parsed = chess.pgn.read_game(io.StringIO(game.pgn))
        name = name_for_moves(list(parsed.mainline_moves())[:30]) if parsed else None
        out.append({"game_id": game.id, "user_color": game.user_color, "opponent": game.opponent,
                    "opponent_elo": game.opponent_elo, "played_at": game.played_at.isoformat(),
                    "opening": name, "deviation": dev})
    return out
