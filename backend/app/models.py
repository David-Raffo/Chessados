from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import DEFAULT_SPLIT
from .db import Base


class AppSetting(Base):
    """Ajustes internos de la instalación (p. ej. el secreto JWT generado si no hay uno en el .env)."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(40), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)  # siempre en minúsculas
    password_hash: Mapped[str] = mapped_column(String(200))
    weekly_hours: Mapped[float] = mapped_column(Float, default=7.0)
    target_split: Mapped[dict] = mapped_column(JSON, default=lambda: dict(DEFAULT_SPLIT))
    ladder_elo: Mapped[int] = mapped_column(Integer, default=1200)
    review_lock: Mapped[bool] = mapped_column(Boolean, default=True)
    endgame_boost_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    lichess_username: Mapped[str | None] = mapped_column(String(80), nullable=True)
    chesscom_username: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # El administrador (la primera cuenta) tiene invitaciones ilimitadas
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    invited_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Invite(Base):
    """Código de invitación de un solo uso para crear cuenta."""

    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    used_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Rating(Base):
    """Historial Glicko-2 por área: la fila más reciente de cada área es el rating actual."""

    __tablename__ = "ratings"
    __table_args__ = (Index("ix_ratings_user_area", "user_id", "area", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    area: Mapped[str] = mapped_column(String(20))
    rating: Mapped[float] = mapped_column(Float)
    rd: Mapped[float] = mapped_column(Float)
    volatility: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    pgn: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(20), default="app")  # app, pgn, lichess, chesscom
    opponent: Mapped[str] = mapped_column(String(80), default="stockfish")
    opponent_elo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_control: Mapped[str | None] = mapped_column(String(20), nullable=True)
    user_color: Mapped[str] = mapped_column(String(5), default="white")
    result: Mapped[str] = mapped_column(String(10), default="*")
    user_result: Mapped[str | None] = mapped_column(String(5), nullable=True)  # win, loss, draw
    ladder: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_status: Mapped[str] = mapped_column(String(10), default="pending", index=True)
    analysis_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis: Mapped[list["GameAnalysis"]] = relationship(
        back_populates="game", cascade="all, delete-orphan", order_by="GameAnalysis.ply"
    )


class GameAnalysis(Base):
    __tablename__ = "game_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    ply: Mapped[int] = mapped_column(Integer)
    san: Mapped[str] = mapped_column(String(12))
    uci: Mapped[str] = mapped_column(String(6))
    fen_before: Mapped[str] = mapped_column(String(100))
    eval_cp: Mapped[int] = mapped_column(Integer)  # tras la jugada, punto de vista blancas
    mate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    best_uci: Mapped[str | None] = mapped_column(String(6), nullable=True)
    best_san: Mapped[str | None] = mapped_column(String(12), nullable=True)
    pv_san: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[str] = mapped_column(String(12))  # best, good, inaccuracy, mistake, blunder
    phase: Mapped[str] = mapped_column(String(12))  # opening, middlegame, endgame
    error_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_user_move: Mapped[bool] = mapped_column(Boolean)

    game: Mapped[Game] = relationship(back_populates="analysis")


class Puzzle(Base):
    __tablename__ = "puzzles"
    # Índice para buscar por tema (ver main.migrate; se crea también en instalaciones nuevas)
    __table_args__ = (
        Index("ix_puzzles_themes", text("string_to_array(themes, ' ')"), postgresql_using="gin"),
    )

    id: Mapped[str] = mapped_column(String(10), primary_key=True)  # id de Lichess
    fen: Mapped[str] = mapped_column(String(100))
    moves: Mapped[str] = mapped_column(Text)
    rating: Mapped[int] = mapped_column(Integer, index=True)
    rating_dev: Mapped[int] = mapped_column(Integer, default=75)
    popularity: Mapped[int] = mapped_column(Integer, default=0)
    nb_plays: Mapped[int] = mapped_column(Integer, default=0)
    themes: Mapped[str] = mapped_column(Text, default="")
    opening_tags: Mapped[str | None] = mapped_column(Text, nullable=True)


class PuzzleAttempt(Base):
    __tablename__ = "puzzle_attempts"
    __table_args__ = (Index("ix_attempts_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    puzzle_id: Mapped[str] = mapped_column(ForeignKey("puzzles.id", ondelete="CASCADE"))
    solved: Mapped[bool] = mapped_column(Boolean)
    seconds: Mapped[float] = mapped_column(Float)
    mode: Mapped[str] = mapped_column(String(12), default="normal")  # normal, rush, woodpecker, review
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PuzzleAssignment(Base):
    """Puzzle en curso por filtro: se mantiene al recargar hasta que lo resuelves o lo fallas."""

    __tablename__ = "puzzle_assignments"
    __table_args__ = (UniqueConstraint("user_id", "filter_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    filter_key: Mapped[str] = mapped_column(String(60))  # área|tema
    puzzle_id: Mapped[str] = mapped_column(ForeignKey("puzzles.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReviewItem(Base):
    """Cola de repetición espaciada (puzzles fallados, líneas de apertura, finales)."""

    __tablename__ = "review_queue"
    __table_args__ = (UniqueConstraint("user_id", "kind", "ref_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(12))  # puzzle, opening, endgame
    ref_id: Mapped[str] = mapped_column(String(40))
    due_date: Mapped[date] = mapped_column(Date, index=True)
    interval: Mapped[int] = mapped_column(Integer, default=1)
    ease: Mapped[float] = mapped_column(Float, default=2.5)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RepertoireLine(Base):
    __tablename__ = "repertoire_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    color: Mapped[str] = mapped_column(String(5))
    fen: Mapped[str] = mapped_column(String(100))
    move: Mapped[str] = mapped_column(String(10))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class TrainingSession(Base):
    """Tiempo activo por área: alimenta horas semanales, rachas y consejos."""

    __tablename__ = "training_sessions"
    __table_args__ = (Index("ix_sessions_user_started", "user_id", "started_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    area: Mapped[str] = mapped_column(String(20))
    activity: Mapped[str] = mapped_column(String(20))  # game, review, puzzles, rush...
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active_seconds: Mapped[int] = mapped_column(Integer, default=0)
    ref_id: Mapped[str | None] = mapped_column(String(40), nullable=True)


class EndgameAttempt(Base):
    __tablename__ = "endgame_attempts"
    __table_args__ = (Index("ix_endgame_user_lesson", "user_id", "lesson_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[str] = mapped_column(String(40))
    success: Mapped[bool] = mapped_column(Boolean)
    seconds: Mapped[float] = mapped_column(Float)
    moves: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WoodpeckerSet(Base):
    """Bloque fijo de puzzles que se repite en ciclos cada vez más rápidos."""

    __tablename__ = "woodpecker_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    puzzle_ids: Mapped[list] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cycles: Mapped[list["WoodpeckerCycle"]] = relationship(
        back_populates="set", cascade="all, delete-orphan", order_by="WoodpeckerCycle.number"
    )


class WoodpeckerCycle(Base):
    __tablename__ = "woodpecker_cycles"

    id: Mapped[int] = mapped_column(primary_key=True)
    set_id: Mapped[int] = mapped_column(ForeignKey("woodpecker_sets.id", ondelete="CASCADE"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer, default=0)  # siguiente puzzle del bloque
    solved: Mapped[int] = mapped_column(Integer, default=0)
    seconds: Mapped[float] = mapped_column(Float, default=0)
    target_days: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    set: Mapped[WoodpeckerSet] = relationship(back_populates="cycles")


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"
    __table_args__ = (UniqueConstraint("user_id", "day", "kind"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[date] = mapped_column(Date)
    kind: Mapped[str] = mapped_column(String(20))  # puzzle, own-game, visual
    success: Mapped[bool] = mapped_column(Boolean)
    score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyPlan(Base):
    """Sesión «Entrenar hoy» fijada al generarse por primera vez en el día."""

    __tablename__ = "daily_plans"
    __table_args__ = (UniqueConstraint("user_id", "day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    steps: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RushRun(Base):
    __tablename__ = "rush_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    minutes: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LessonProgress(Base):
    """Avance en una lección de Aprender: paso en el que te quedaste y si la has completado."""

    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[str] = mapped_column(String(40))
    step: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    best_mistakes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
