"""Comprueba las lecciones de Aprender con Stockfish antes de publicarlas.

    docker compose exec worker python -m app.check_learn            # todos los cursos
    docker compose exec worker python -m app.check_learn tactica    # solo un curso
    docker compose exec worker python -m app.check_learn finales_basicos   # solo un fichero de learn_data

- Formato: campos obligatorios de cada paso, ids únicos y presentes en el temario del curso.
- Todas las posiciones son legales y las jugadas de `moves` y `line` también.
- select: la casilla existe; con "mate": True, ir a ella da mate.
- move: cada jugada tuya es la mejor según Stockfish y claramente mejor que la segunda
  (si es mate, la única con ese mate más rápido; si no, al menos 1 peón mejor, o lo que diga «margin»).
  La línea acaba en mate si su última jugada lleva «#» y, si no, con ventaja clara (al menos +1,5, o lo
  que diga «min_eval») para quien la juega.
  Si la respuesta del rival no es la que prefiere Stockfish, se avisa.
- choice: exactamente una opción correcta.
- practice: hay al menos 50 puzzles del tema en la base de datos.
- play: si hay que ganar o dar mate, la posición está ganada para quien juega (al menos +4, o mate);
  si hay que hacer tablas, no está perdida (−1 o mejor).
"""

import importlib
import sys

import chess
import chess.engine
from sqlalchemy import func, select

from .config import STOCKFISH_PATH

DEPTH = 22
UNIQUE_CP = 100  # ventaja mínima de la jugada pedida sobre la segunda mejor
WIN_CP = 150  # ventaja mínima al final de una línea que no acaba en mate
SQUARES = set(chess.SQUARE_NAMES)
COLORS = {"green", "red", "blue", "yellow"}
REQUIRED = {
    "explain": {"text", "fen"},
    "select": {"text", "fen", "answer", "success"},
    "move": {"text", "fen", "line", "hint", "success"},
    "choice": {"text", "fen", "options"},
    "practice": {"text", "theme", "count"},
    "play": {"text", "fen", "goal", "moves", "hint", "success"},
}


class Checker:
    def __init__(self) -> None:
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.failures = 0

    def fail(self, where: str, msg: str) -> None:
        self.failures += 1
        print(f"FAIL {where}: {msg}")

    def score(self, board: chess.Board, n: int = 5) -> list[tuple[chess.Move, chess.engine.PovScore]]:
        infos = self.engine.analyse(board, chess.engine.Limit(depth=DEPTH), multipv=n)
        return [(i["pv"][0], i["score"].pov(board.turn)) for i in infos]

    def check_shapes(self, where: str, st: dict) -> None:
        for arrow in st.get("arrows", []):
            if len(arrow) != 3 or arrow[0] not in SQUARES or arrow[1] not in SQUARES or arrow[2] not in COLORS:
                self.fail(where, f"flecha mal formada {arrow}")
        for sq, color in st.get("squares", {}).items():
            if sq not in SQUARES or color not in COLORS:
                self.fail(where, f"casilla mal formada {sq}: {color}")

    def check_move(self, where: str, st: dict) -> None:
        b = chess.Board(st["fen"])
        mover = b.turn
        for i, san in enumerate(st["line"]):
            try:
                expected = b.parse_san(san)
            except ValueError:
                self.fail(where, f"jugada ilegal {san} en {b.fen()}")
                return
            top = self.score(b)
            best_move, best = top[0]
            if i % 2 == 0:
                if best.is_mate() and best.mate() > 0:
                    fastest = [m for m, s in top if s == best]
                    if fastest != [expected] and not self._gives_mate(b, expected):
                        names = [b.san(m) for m in fastest]
                        self.fail(where, f"{san}: el mate más rápido no es solo esta jugada ({names})")
                else:
                    if best_move != expected:
                        self.fail(where, f"{san} no es la mejor: Stockfish prefiere {b.san(best_move)} ({best})")
                    elif len(top) > 1:
                        gap = best.score(mate_score=100000) - top[1][1].score(mate_score=100000)
                        if gap < st.get("margin", UNIQUE_CP):
                            self.fail(where, f"{san} no destaca: {b.san(top[1][0])} es casi igual de buena ({top[1][1]} frente a {best})")
            elif best_move != expected:
                print(f"aviso {where}: el rival juega {san}, Stockfish prefiere {b.san(best_move)}")
            b.push(expected)
        if st["line"][-1].endswith("#"):
            if not b.is_checkmate():
                self.fail(where, "la línea acaba en «#» pero no es mate")
        else:
            final = self.engine.analyse(b, chess.engine.Limit(depth=DEPTH))["score"].pov(mover)
            if final.score(mate_score=100000) < st.get("min_eval", WIN_CP):
                self.fail(where, f"al final de la línea la ventaja no es clara ({final})")

    def check_play(self, where: str, st: dict) -> None:
        b = chess.Board(st["fen"])
        color = st.get("color")
        me = (color == "white") if color else b.turn
        if st["goal"] not in ("mate", "win", "draw"):
            self.fail(where, f"objetivo desconocido {st['goal']}")
            return
        score = self.engine.analyse(b, chess.engine.Limit(depth=DEPTH))["score"].pov(me)
        value = score.score(mate_score=100000)
        if st["goal"] in ("mate", "win") and value < st.get("min_eval", 400):
            self.fail(where, f"hay que ganar, pero Stockfish no lo ve ganado ({score})")
        if st["goal"] == "draw" and value < -100:
            self.fail(where, f"hay que hacer tablas, pero la posición está perdida ({score})")

    @staticmethod
    def _gives_mate(board: chess.Board, move: chess.Move) -> bool:
        board.push(move)
        mate = board.is_checkmate()
        board.pop()
        return mate

    def check_lesson(self, lesson: dict, course: str, outline_ids: set[str], themes: set[str], db) -> None:
        lid = lesson.get("id", "?")
        failures_before = self.failures
        for key in ("id", "course", "title", "summary", "minutes", "steps"):
            if key not in lesson:
                self.fail(lid, f"falta «{key}»")
        if lesson.get("course") != course:
            self.fail(lid, f"course «{lesson.get('course')}» no es «{course}»")
        if lid not in outline_ids:
            self.fail(lid, "el id no está en el temario de COURSES (app/learn.py)")
        for n, st in enumerate(lesson.get("steps", []), 1):
            where = f"{lid} paso {n}"
            kind = st.get("type")
            if kind not in REQUIRED:
                self.fail(where, f"tipo desconocido {kind}")
                continue
            missing = REQUIRED[kind] - st.keys()
            if missing:
                self.fail(where, f"faltan {sorted(missing)}")
                continue
            if len(st["text"]) > 450:
                print(f"aviso {where}: texto largo ({len(st['text'])} caracteres)")
            if "fen" in st:
                b = chess.Board(st["fen"])
                if not b.is_valid():
                    self.fail(where, f"posición no válida {st['fen']}")
                    continue
                if st.get("orientation", "white") not in ("white", "black"):
                    self.fail(where, "orientation debe ser white o black")
            self.check_shapes(where, st)
            if kind == "explain":
                for m in st.get("moves", []):
                    try:
                        b.push_san(m["san"])
                    except ValueError:
                        self.fail(where, f"jugada ilegal {m['san']}")
                        break
            elif kind == "select":
                if st["answer"] not in SQUARES:
                    self.fail(where, f"casilla {st['answer']} no existe")
                elif st.get("mate"):
                    mates = [m for m in b.legal_moves if chess.square_name(m.to_square) == st["answer"] and self._gives_mate(b, m)]
                    if not mates:
                        self.fail(where, f"ir a {st['answer']} no da mate")
                for sq in st.get("wrong", {}):
                    if sq not in SQUARES or sq == st["answer"]:
                        self.fail(where, f"casilla de «wrong» no válida: {sq}")
            elif kind == "move":
                self.check_move(where, st)
            elif kind == "choice":
                right = [o for o in st["options"] if o.get("correct")]
                if len(right) != 1:
                    self.fail(where, f"{len(right)} opciones correctas (debe haber una)")
                for o in st["options"]:
                    if not o.get("text") or not o.get("why"):
                        self.fail(where, "cada opción necesita «text» y «why»")
            elif kind == "play":
                self.check_play(where, st)
            elif kind == "practice":
                from .models import Puzzle  # import diferido: solo hace falta la base de datos aquí

                n_puzzles = db.scalar(select(func.count()).select_from(Puzzle).where(
                    (" " + Puzzle.themes + " ").like(f"% {st['theme']} %")))
                if n_puzzles < 50:
                    self.fail(where, f"solo hay {n_puzzles} puzzles del tema {st['theme']}")
        theme = lesson.get("theme")
        if theme and theme not in themes:
            print(f"aviso {lid}: el tema «{theme}» no coincide con el del temario")
        print(f"{'ok  ' if self.failures == failures_before else 'MAL '}{lid}: {len(lesson.get('steps', []))} pasos revisados")

    def run(self, courses: list[str]) -> int:
        from .db import SessionLocal
        from .learn import COURSES

        db = SessionLocal()
        seen: set[str] = set()
        ids = {c["id"] for c in COURSES}
        # Un fichero suelto de learn_data cuenta como su curso, pero solo con sus lecciones
        files = {a: importlib.import_module(f"app.learn_data.{a}") for a in courses if a not in ids}
        for course in COURSES:
            sub = [m for m in files.values() if any(l.get("course") == course["id"] for l in m.LESSONS)]
            if courses and course["id"] not in courses and not sub:
                continue
            module = sub[0] if sub else importlib.import_module(f"app.learn_data.{course['id']}")
            outline_ids = {lid for lid, _, _ in course["outline"]}
            themes = {t for _, _, t in course["outline"] if t}
            print(f"== {course['title']}: {len(module.LESSONS)} de {len(outline_ids)} lecciones")
            for lesson in module.LESSONS:
                if lesson.get("id") in seen:
                    self.fail(lesson["id"], "id repetido")
                seen.add(lesson.get("id"))
                self.check_lesson(lesson, course["id"], outline_ids, themes, db)
        db.close()
        self.engine.quit()
        print("TODO OK" if not self.failures else f"HAY {self.failures} FALLOS")
        return 0 if not self.failures else 1


if __name__ == "__main__":
    raise SystemExit(Checker().run(sys.argv[1:]))
