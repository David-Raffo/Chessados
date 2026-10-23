"""Comprueba las lecciones de Aprender con Stockfish antes de publicarlas.

    docker compose exec worker python -m app.check_learn

- Todas las posiciones son legales.
- En los pasos «select», ir a la casilla pedida da mate.
- En los pasos «move», cada jugada tuya es la única con la mejor evaluación y la línea acaba en mate.
  Si la respuesta del rival no es la que prefiere Stockfish, se avisa.
"""

import chess
import chess.engine

from .config import STOCKFISH_PATH
from .learn import LESSONS


def gives_mate(board: chess.Board, move: chess.Move) -> bool:
    board.push(move)
    mate = board.is_checkmate()
    board.pop()
    return mate


def main() -> None:
    eng = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    ok = True
    for lesson in LESSONS:
        for n, st in enumerate(lesson["steps"], 1):
            if "fen" in st:
                b = chess.Board(st["fen"])
                if not b.is_valid():
                    print(f"FAIL {lesson['id']} paso {n}: FEN no válido")
                    ok = False
                    continue
            if st["type"] == "explain" and st.get("moves"):
                for m in st["moves"]:
                    b.push_san(m["san"])
            if st["type"] == "select":
                b = chess.Board(st["fen"])
                mates = [m for m in b.legal_moves if chess.square_name(m.to_square) == st["answer"] and gives_mate(b, m)]
                print(f"{'OK  ' if mates else 'FAIL'} {lesson['id']} paso {n}: ir a {st['answer']} da mate")
                ok &= bool(mates)
            if st["type"] == "move":
                b = chess.Board(st["fen"])
                for i, san in enumerate(st["line"]):
                    if i % 2 == 0:
                        infos = eng.analyse(b, chess.engine.Limit(depth=24), multipv=5)
                        best = infos[0]["score"].pov(b.turn)
                        tops = [b.san(x["pv"][0]) for x in infos if x["score"].pov(b.turn) == best]
                        unique = tops == [b.san(b.parse_san(san))]
                        if not unique:
                            print(f"FAIL {lesson['id']} paso {n}: {san} no es la única mejor ({tops})")
                            ok = False
                    else:
                        infos = eng.analyse(b, chess.engine.Limit(depth=24), multipv=3)
                        if b.san(infos[0]["pv"][0]) != b.san(b.parse_san(san)):
                            print(f"aviso {lesson['id']} paso {n}: el rival juega {san}, Stockfish prefiere {b.san(infos[0]['pv'][0])}")
                    b.push_san(san)
                mate = b.is_checkmate()
                print(f"{'OK  ' if mate else 'FAIL'} {lesson['id']} paso {n}: línea {' '.join(st['line'])} termina en mate")
                ok &= mate
    eng.quit()
    print("TODO OK" if ok else "HAY FALLOS")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
