import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Chess } from "chess.js";
import confetti from "canvas-confetti";
import Board, { isPromotion, toDests, turnColor, uciToKeys, type Color, type DrawShape, type Key } from "../components/Board";
import Promotion from "../components/Promotion";
import { api } from "../lib/api";
import { Engine } from "../lib/engine";
import { sound } from "../lib/sound";
import { useActivity } from "../lib/useActivity";

export interface Lesson {
  id: string;
  level: string;
  title: string;
  rating: number;
  fen: string;
  color: Color;
  goal: "mate" | "win" | "draw";
  moves: number;
  tip: string;
  attempts: number;
  successes: number;
  due: boolean;
  next_review: string | null;
}

const GOAL_TEXT = {
  mate: "Da jaque mate",
  win: "Gana: da mate o deja al rival solo con el rey",
  draw: "Consigue las tablas",
};

export default function Endgames() {
  const { id } = useParams();
  const [data, setData] = useState<{ lessons: Lesson[]; rating: number } | null>(null);

  const load = useCallback(() => {
    api<{ lessons: Lesson[]; rating: number }>("/endgames").then(setData).catch(() => undefined);
  }, []);
  useEffect(load, [load]);

  if (!data) return <p className="text-muted">Cargando lecciones…</p>;
  const lesson = data.lessons.find((l) => l.id === id);
  if (id && lesson) return <LessonView key={lesson.id} lesson={lesson} lessons={data.lessons} onDone={load} />;

  const levels = [...new Set(data.lessons.map((l) => l.level))];
  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold">Finales</h1>
          <p className="text-muted">Posiciones teóricas contra Stockfish a máxima fuerza. Repítelas hasta que salgan solas.</p>
        </div>
        <div className="card px-4 py-2 text-right">
          <div className="text-2xl font-extrabold text-endgames">{data.rating}</div>
          <div className="text-xs text-muted">ELO de finales</div>
        </div>
      </header>
      {levels.map((level) => (
        <section key={level} className="space-y-2">
          <h2 className="font-bold">{level}</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.lessons
              .filter((l) => l.level === level)
              .map((l) => (
                <Link key={l.id} to={`/finales/${l.id}`} className="card transition hover:bg-panel2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-semibold">{l.title}</div>
                    {l.due ? (
                      <span className="rounded-full bg-endgames/20 px-2 py-0.5 text-xs font-semibold text-endgames">Repasar</span>
                    ) : l.successes > 0 ? (
                      <span className="text-good">✓</span>
                    ) : null}
                  </div>
                  <div className="mt-1 text-sm text-muted">
                    {l.color === "white" ? "Blancas" : "Negras"} · {GOAL_TEXT[l.goal].split(":")[0]} · {l.rating}
                  </div>
                  <div className="mt-1 text-xs text-muted">
                    {l.attempts ? `${l.successes}/${l.attempts} conseguidos` : "Sin intentar"}
                  </div>
                </Link>
              ))}
          </div>
        </section>
      ))}
      <div className="card flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted">¿Quieres más práctica? Puzzles de finales reales de Lichess, con su propio ELO.</p>
        <Link to="/puzzles?area=endgames&theme=endgame" className="btn-ghost">
          Puzzles de finales
        </Link>
      </div>
    </div>
  );
}

type Status = "playing" | "won" | "lost";

/** ¿Tiene el bando `color` solo el rey? */
function bareKing(chess: Chess, color: "w" | "b") {
  return chess.board().flat().filter((p) => p && p.color === color).length === 1;
}

function LessonView({ lesson, lessons, onDone }: { lesson: Lesson; lessons: Lesson[]; onDone: () => void }) {
  const navigate = useNavigate();
  const chess = useRef(new Chess(lesson.fen));
  const engine = useRef<Engine | null>(null);
  const [fen, setFen] = useState(lesson.fen);
  const [lastMove, setLastMove] = useState<Key[] | undefined>();
  const [status, setStatus] = useState<Status>("playing");
  const [reason, setReason] = useState("");
  const [userMoves, setUserMoves] = useState(0);
  const [thinking, setThinking] = useState(false);
  const [promo, setPromo] = useState<{ from: Key; to: Key } | null>(null);
  const [hint, setHint] = useState<DrawShape[]>([]);
  const [result, setResult] = useState<{ rating_before: number; rating_after: number; next_review: string } | null>(null);
  const [round, setRound] = useState(0);
  const started = useRef(performance.now());
  const finished = useRef(false);
  const me = lesson.color === "white" ? "w" : "b";
  useActivity(status === "playing" ? "endgames" : null, "lesson", lesson.id);

  const finish = useCallback(
    (success: boolean, why: string, moves: number) => {
      if (finished.current) return;
      finished.current = true;
      setStatus(success ? "won" : "lost");
      setReason(why);
      if (success) {
        sound.good();
        confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 }, disableForReducedMotion: true });
      } else sound.bad();
      api(`/endgames/${lesson.id}/attempt`, {
        body: { success, seconds: (performance.now() - started.current) / 1000, moves },
      })
        .then((r) => {
          setResult(r);
          onDone();
        })
        .catch(() => undefined);
    },
    [lesson.id, onDone],
  );

  /** Comprueba el objetivo tras cualquier jugada. Devuelve true si la lección ha terminado. */
  const check = useCallback(
    async (moves: number): Promise<boolean> => {
      const c = chess.current;
      if (c.isCheckmate()) {
        const userMated = c.turn() === me;
        if (userMated) finish(false, "Te han dado mate.", moves);
        else finish(lesson.goal !== "draw", lesson.goal === "draw" ? "Has dado mate… pero el objetivo eran tablas." : "¡Jaque mate!", moves);
        return true;
      }
      if (c.isDraw()) {
        const why = c.isStalemate() ? "Rey ahogado." : c.isThreefoldRepetition() ? "Triple repetición." : c.isInsufficientMaterial() ? "Material insuficiente." : "Regla de los 50 movimientos.";
        finish(lesson.goal === "draw", lesson.goal === "draw" ? `¡Tablas! ${why}` : `Tablas: ${why} Había que ganar.`, moves);
        return true;
      }
      const opp = me === "w" ? "b" : "w";
      if (lesson.goal === "win" && c.turn() === opp && bareKing(c, opp)) {
        // Victoria si conservas dama o torre y el rival no puede capturarla en su jugada
        const heavy = c.board().flat().filter((p) => p && p.color === me && (p.type === "q" || p.type === "r"));
        const canCapture = c.moves({ verbose: true }).some((m) => m.captured === "q" || m.captured === "r");
        if (heavy.length && !canCapture) {
          finish(true, "El rival se ha quedado solo con el rey: victoria asegurada.", moves);
          return true;
        }
      }
      if (moves >= lesson.moves && c.turn() !== me) {
        if (lesson.goal === "draw") {
          // Has aguantado: se comprueba que la posición no esté perdida
          const { cp } = await engine.current!.evaluate(c.fen(), 14);
          const mine = me === "w" ? cp : -cp;
          finish(mine >= -150, mine >= -150 ? "Has aguantado: la posición es de tablas." : "Has aguantado, pero la posición está perdida.", moves);
        } else {
          finish(false, `Se acabaron las ${lesson.moves} jugadas.`, moves);
        }
        return true;
      }
      return false;
    },
    [finish, lesson.goal, lesson.moves, me],
  );

  const engineMove = useCallback(
    async (moves: number) => {
      const eng = engine.current;
      if (!eng || finished.current) return;
      setThinking(true);
      try {
        const uci = await eng.bestMove(chess.current.fen(), "movetime 500");
        if (finished.current || !uci || uci === "(none)") return;
        const [from, to] = uciToKeys(uci);
        const m = chess.current.move({ from, to, promotion: uci[4] ?? "q" });
        setLastMove([from, to]);
        setFen(chess.current.fen());
        if (chess.current.inCheck()) sound.check();
        else if (m.captured) sound.capture();
        else sound.move();
        await check(moves);
      } finally {
        setThinking(false);
      }
    },
    [check],
  );

  useEffect(() => {
    const eng = new Engine();
    engine.current = eng;
    finished.current = false;
    eng
      .setOptions([["UCI_LimitStrength", "false"], ["Skill Level", 20], ["Hash", 32]])
      .then(() => eng.newGame())
      .then(() => {
        if (chess.current.turn() !== me) engineMove(0);
      });
    return () => {
      eng.terminate();
      engine.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [round]);

  async function play(from: Key, to: Key, promotion?: string) {
    if (status !== "playing" || thinking) return;
    if (!promotion && isPromotion(chess.current, from, to)) {
      setPromo({ from, to });
      return;
    }
    let m;
    try {
      m = chess.current.move({ from, to, promotion });
    } catch {
      setFen(chess.current.fen());
      return;
    }
    setHint([]);
    setLastMove([from, to]);
    setFen(chess.current.fen());
    if (chess.current.inCheck()) sound.check();
    else if (m.captured) sound.capture();
    else sound.move();
    const moves = userMoves + 1;
    setUserMoves(moves);
    if (!(await check(moves))) engineMove(moves);
  }

  async function showHint() {
    if (!engine.current || status !== "playing") return;
    const { pv } = await engine.current.evaluate(chess.current.fen(), 16);
    if (pv[0]) {
      const [orig, dest] = uciToKeys(pv[0]);
      setHint([{ orig, dest, brush: "green" }]);
    }
  }

  function restart() {
    chess.current = new Chess(lesson.fen);
    finished.current = false;
    started.current = performance.now();
    setFen(lesson.fen);
    setLastMove(undefined);
    setStatus("playing");
    setReason("");
    setUserMoves(0);
    setHint([]);
    setResult(null);
    setRound((r) => r + 1);
  }

  const next = lessons[lessons.findIndex((l) => l.id === lesson.id) + 1];
  const dests = useMemo(() => toDests(chess.current), [fen]);
  const userTurn = status === "playing" && !thinking && turnColor(chess.current) === lesson.color;
  const delta = result ? result.rating_after - result.rating_before : 0;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
      <div className="mx-auto w-full max-w-[min(100%,calc(100vh-8rem))]">
        <div className="relative">
          <Board
            fen={fen}
            orientation={lesson.color}
            movable={userTurn ? lesson.color : undefined}
            dests={dests}
            lastMove={lastMove}
            check={chess.current.inCheck()}
            shapes={hint}
            onMove={(f, t) => play(f, t)}
          />
          {promo && (
            <Promotion
              color={lesson.color}
              onPick={(role) => {
                const p = promo;
                setPromo(null);
                play(p.from, p.to, role);
              }}
              onCancel={() => {
                setPromo(null);
                setFen(chess.current.fen());
              }}
            />
          )}
        </div>
      </div>
      <aside className="space-y-4">
        <div className="card space-y-3">
          <div>
            <div className="text-sm font-semibold text-endgames">{lesson.level}</div>
            <h1 className="text-xl font-extrabold">{lesson.title}</h1>
          </div>
          <div className="rounded-xl bg-panel2 p-3 text-sm">
            <div className="font-semibold">
              Juegas con {lesson.color === "white" ? "blancas" : "negras"}. {GOAL_TEXT[lesson.goal]}.
            </div>
            <div className="mt-1 text-muted">
              {lesson.goal === "draw"
                ? `Aguanta ${lesson.moves} jugadas (${Math.max(0, lesson.moves - userMoves)} restantes).`
                : `Máximo ${lesson.moves} jugadas (${Math.max(0, lesson.moves - userMoves)} restantes).`}
            </div>
          </div>
          <p className="text-sm">💡 {lesson.tip}</p>

          {status === "playing" ? (
            <>
              {thinking && <p className="animate-pulse text-sm text-muted">Stockfish piensa…</p>}
              <div className="flex gap-2">
                <button className="btn-ghost flex-1" onClick={showHint} disabled={!userTurn}>
                  Pista
                </button>
                <button className="btn-ghost flex-1" onClick={restart}>
                  Reiniciar
                </button>
              </div>
            </>
          ) : (
            <div className="animate-pop space-y-3">
              <div className={`rounded-xl p-3 font-semibold ${status === "won" ? "bg-good/15 text-good" : "bg-bad/15 text-bad"}`}>
                {status === "won" ? "¡Conseguido! " : "No lo has conseguido. "}
                <span className="font-normal">{reason}</span>
              </div>
              {result && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted">ELO de finales</span>
                  <span className="font-bold">
                    {result.rating_after}{" "}
                    <span className={delta > 0 ? "text-good" : delta < 0 ? "text-bad" : "text-muted"}>
                      {delta > 0 ? `+${delta}` : delta || "±0"}
                    </span>
                  </span>
                </div>
              )}
              {result && (
                <p className="text-xs text-muted">
                  Próximo repaso: {new Date(result.next_review).toLocaleDateString("es-ES", { day: "numeric", month: "long" })}
                </p>
              )}
              <div className="flex gap-2">
                <button className="btn-ghost flex-1" onClick={restart}>
                  Repetir
                </button>
                {next ? (
                  <button className="btn-primary flex-1" onClick={() => navigate(`/finales/${next.id}`)}>
                    Siguiente
                  </button>
                ) : (
                  <Link className="btn-primary flex-1" to="/finales">
                    Lecciones
                  </Link>
                )}
              </div>
            </div>
          )}
        </div>
        <Link to="/finales" className="block text-center text-sm text-muted underline">
          Todas las lecciones
        </Link>
      </aside>
    </div>
  );
}
