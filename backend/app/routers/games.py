import io
from datetime import datetime, timezone

import chess.pgn
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..coach import review_locked
from ..db import get_db
from ..models import Game, User
from ..services import apply_result

router = APIRouter(prefix="/api/games", tags=["partidas"])

ENGINE_RD = 60.0  # el rating del rival motor se considera bastante fiable
LADDER_WIN, LADDER_LOSS = 50, 25


def user_result(result: str, color: str) -> str | None:
    if result == "1/2-1/2":
        return "draw"
    if result in ("1-0", "0-1"):
        return "win" if (result == "1-0") == (color == "white") else "loss"
    return None


def game_out(g: Game, with_analysis: bool = False) -> dict:
    out = {
        "id": g.id,
        "pgn": g.pgn,
        "source": g.source,
        "opponent": g.opponent,
        "opponent_elo": g.opponent_elo,
        "time_control": g.time_control,
        "user_color": g.user_color,
        "result": g.result,
        "user_result": g.user_result,
        "reviewed": g.reviewed,
        "user_notes": g.user_notes,
        "analysis_status": g.analysis_status,
        "accuracy": g.accuracy,
        "played_at": g.played_at.isoformat() if g.played_at else None,
    }
    if with_analysis:
        out["analysis"] = [
            {
                "ply": a.ply, "san": a.san, "uci": a.uci, "fen_before": a.fen_before,
                "eval_cp": a.eval_cp, "mate": a.mate, "best_uci": a.best_uci, "best_san": a.best_san,
                "pv_san": a.pv_san, "classification": a.classification, "phase": a.phase,
                "error_type": a.error_type, "is_user_move": a.is_user_move,
            }
            for a in g.analysis
        ]
    return out


def get_own_game(db: Session, user: User, game_id: int) -> Game:
    g = db.get(Game, game_id)
    if not g or g.user_id != user.id:
        raise HTTPException(404, "Partida no encontrada")
    return g


@router.get("/can-play")
def can_play(user: User = Depends(current_user), db: Session = Depends(get_db)):
    g = review_locked(db, user)
    return {"locked": g is not None, "game_id": g.id if g else None, "ladder_elo": user.ladder_elo}


class GameIn(BaseModel):
    pgn: str = Field(max_length=200_000)
    user_color: str = Field(pattern="^(white|black)$")
    result: str = Field(pattern=r"^(1-0|0-1|1/2-1/2)$")
    opponent: str = "stockfish"
    opponent_elo: int = Field(ge=100, le=3500)
    time_control: str | None = None
    ladder: bool = False


@router.post("")
def save_game(body: GameIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ures = user_result(body.result, body.user_color)
    g = Game(
        user_id=user.id, pgn=body.pgn, source="app", opponent=body.opponent, opponent_elo=body.opponent_elo,
        time_control=body.time_control, user_color=body.user_color, result=body.result, user_result=ures,
        ladder=body.ladder, analysis_status="pending",
    )
    db.add(g)
    score = {"win": 1.0, "draw": 0.5, "loss": 0.0}[ures]
    before, after = apply_result(db, user.id, "play", body.opponent_elo, ENGINE_RD, score)
    ladder_before = user.ladder_elo
    if body.ladder:
        if ures == "win":
            user.ladder_elo = min(3000, user.ladder_elo + LADDER_WIN)
        elif ures == "loss":
            user.ladder_elo = max(400, user.ladder_elo - LADDER_LOSS)
    db.commit()
    return {
        "game": game_out(g),
        "rating_before": round(before),
        "rating_after": round(after),
        "ladder_before": ladder_before,
        "ladder_after": user.ladder_elo,
    }


@router.get("")
def list_games(limit: int = 50, user: User = Depends(current_user), db: Session = Depends(get_db)):
    games = db.scalars(
        select(Game).where(Game.user_id == user.id).order_by(Game.played_at.desc()).limit(min(limit, 200))
    ).all()
    return [game_out(g) for g in games]


@router.get("/{game_id}")
def get_game(game_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return game_out(get_own_game(db, user, game_id), with_analysis=True)


class GamePatch(BaseModel):
    user_notes: str | None = Field(default=None, max_length=10_000)
    reviewed: bool | None = None


@router.patch("/{game_id}")
def patch_game(game_id: int, body: GamePatch, user: User = Depends(current_user), db: Session = Depends(get_db)):
    g = get_own_game(db, user, game_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(g, k, v)
    db.commit()
    return game_out(g)


@router.delete("/{game_id}")
def delete_game(game_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(get_own_game(db, user, game_id))
    db.commit()
    return {"ok": True}


@router.post("/{game_id}/reanalyze")
def reanalyze(game_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    g = get_own_game(db, user, game_id)
    g.analysis_status = "pending"
    db.commit()
    return game_out(g)


# --- Importación -----------------------------------------------------------


def _parse_date(headers: chess.pgn.Headers) -> datetime | None:
    d = headers.get("UTCDate") or headers.get("Date") or ""
    t = headers.get("UTCTime") or "12:00:00"
    try:
        return datetime.strptime(f"{d} {t}", "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def import_pgn_text(db: Session, user: User, text: str, source: str, username: str | None) -> dict:
    stream = io.StringIO(text)
    imported = skipped = 0
    existing = set(db.scalars(select(Game.external_id).where(Game.user_id == user.id, Game.external_id.isnot(None))))
    while True:
        game = chess.pgn.read_game(stream)
        if game is None:
            break
        h = game.headers
        moves = list(game.mainline_moves())
        ext = (h.get("Link") or h.get("Site")) if source != "pgn" else None
        if len(moves) < 6 or (ext and ext in existing):
            skipped += 1
            continue
        color = "white"
        if username and h.get("Black", "").lower() == username.lower():
            color = "black"
        opp_name = h.get("Black" if color == "white" else "White", "?")
        opp_elo = h.get("BlackElo" if color == "white" else "WhiteElo", "")
        result = h.get("Result", "*")
        exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
        g = Game(
            user_id=user.id, pgn=game.accept(exporter), source=source, opponent=opp_name[:80],
            opponent_elo=int(opp_elo) if opp_elo.isdigit() else None, time_control=h.get("TimeControl"),
            user_color=color, result=result, user_result=user_result(result, color),
            analysis_status="pending", external_id=ext,
        )
        if (played := _parse_date(h)) is not None:
            g.played_at = played
        db.add(g)
        if ext:
            existing.add(ext)
        imported += 1
    db.commit()
    return {"imported": imported, "skipped": skipped}


class PgnIn(BaseModel):
    pgn: str = Field(max_length=2_000_000)
    username: str | None = None


class ExternalIn(BaseModel):
    username: str = Field(min_length=2, max_length=60, pattern=r"^[A-Za-z0-9_-]+$")
    max: int = Field(default=20, ge=1, le=100)


@router.post("/import/pgn")
def import_pgn(body: PgnIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return import_pgn_text(db, user, body.pgn, "pgn", body.username or user.lichess_username)


@router.post("/import/lichess")
def import_lichess(body: ExternalIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    url = f"https://lichess.org/api/games/user/{body.username}"
    try:
        # Sin cabecera Accept: Lichess devuelve PGN por defecto (con Accept explícito responde 404)
        r = httpx.get(url, params={"max": body.max, "clocks": "false", "evals": "false"},
                      headers={"User-Agent": "chessados-trainer/0.1 (autoalojado)"}, timeout=60)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"No se pudo conectar con Lichess: {e}")
    if r.status_code == 404:
        raise HTTPException(404, "Usuario de Lichess no encontrado")
    r.raise_for_status()
    return import_pgn_text(db, user, r.text, "lichess", body.username)


@router.post("/import/chesscom")
def import_chesscom(body: ExternalIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    headers = {"User-Agent": "chessados-trainer/0.1 (autoalojado)"}
    base = f"https://api.chess.com/pub/player/{body.username.lower()}/games/archives"
    try:
        with httpx.Client(headers=headers, timeout=60) as client:
            r = client.get(base)
            if r.status_code == 404:
                raise HTTPException(404, "Usuario de Chess.com no encontrado")
            r.raise_for_status()
            pgns: list[str] = []
            for archive in reversed(r.json().get("archives", [])):
                month = client.get(archive)
                month.raise_for_status()
                for g in reversed(month.json().get("games", [])):
                    if g.get("pgn") and g.get("rules", "chess") == "chess":
                        pgns.append(g["pgn"])
                    if len(pgns) >= body.max:
                        break
                if len(pgns) >= body.max:
                    break
    except httpx.HTTPError as e:
        raise HTTPException(502, f"No se pudo conectar con Chess.com: {e}")
    return import_pgn_text(db, user, "\n\n".join(pgns), "chesscom", body.username)
