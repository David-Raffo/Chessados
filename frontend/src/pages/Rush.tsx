import { useCallback, useEffect, useRef, useState } from "react";
import confetti from "canvas-confetti";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Board from "../components/Board";
import Promotion from "../components/Promotion";
import { api } from "../lib/api";
import { formatClock } from "../lib/labels";
import type { Puzzle } from "../lib/types";
import { usePuzzle } from "../lib/usePuzzle";
import { useActivity } from "../lib/useActivity";

interface History {
  best: Record<string, number>;
  runs: { id: number; minutes: number; score: number; date: string }[];
}

interface Attempt {
  puzzle_id: string;
  solved: boolean;
  seconds: number;
}

const MAX_STRIKES = 3;

export default function Rush() {
  const [history, setHistory] = useState<History | null>(null);
  const [minutes, setMinutes] = useState(3);
  const [run, setRun] = useState<{ puzzles: Puzzle[]; key: number } | null>(null);
  const [final, setFinal] = useState<{ score: number; best: number; is_record: boolean; rating: number } | null>(null);
  const [error, setError] = useState("");

  const loadHistory = useCallback(() => {
    api<History>("/puzzles/rush/history").then(setHistory).catch(() => undefined);
  }, []);
  useEffect(loadHistory, [loadHistory]);

  async function start() {
    setError("");
    setFinal(null);
    try {
      const r = await api<{ puzzles: Puzzle[] }>("/puzzles/rush");
      setRun({ puzzles: r.puzzles, key: Date.now() });
    } catch (e) {
      setError((e as Error).message);
    }
  }

  if (run) {
    return (
      <RushRun
        key={run.key}
        puzzles={run.puzzles}
        minutes={minutes}
        onFinish={(score, attempts) => {
          setRun(null);
          api<{ best: number; is_record: boolean; rating: number }>("/puzzles/rush/finish", {
            body: { minutes, score, attempts },
          })
            .then((r) => {
              setFinal({ score, ...r });
              if (r.is_record && score > 0) confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 }, disableForReducedMotion: true });
              loadHistory();
            })
            .catch((e) => setError(e.message));
        }}
      />
    );
  }

  const runs = (history?.runs ?? []).filter((r) => r.minutes === minutes).map((r, i) => ({ ...r, n: i + 1 }));

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <header>
        <h1 className="text-2xl font-extrabold">Contrarreloj</h1>
        <p className="text-muted">Resuelve todos los que puedas. Dificultad creciente; tres fallos y fuera.</p>
      </header>

      {final && (
        <div className="card animate-pop text-center">
          <div className="text-sm text-muted">Puntuación</div>
          <div className="text-6xl font-extrabold text-rush">{final.score}</div>
          {final.is_record && final.score > 0 ? (
            <div className="font-semibold text-good">¡Nuevo récord personal!</div>
          ) : (
            <div className="text-muted">Récord: {final.best}</div>
          )}
          <div className="mt-1 text-sm text-muted">ELO de contrarreloj: {final.rating}</div>
        </div>
      )}

      <section className="card space-y-4">
        <div className="grid grid-cols-2 gap-2">
          {[3, 5].map((m) => (
            <button
              key={m}
              onClick={() => setMinutes(m)}
              className={`rounded-xl border p-4 text-left ${minutes === m ? "border-rush bg-rush/10" : "border-line"}`}
            >
              <div className="text-2xl font-extrabold">{m} min</div>
              <div className="text-sm text-muted">Récord: {history?.best?.[m] ?? "—"}</div>
            </button>
          ))}
        </div>
        {error && <p className="text-sm text-bad">{error}</p>}
        <button className="btn-primary w-full py-3 text-lg" onClick={start}>
          ¡Empezar!
        </button>
      </section>

      {runs.length > 1 && (
        <section className="card">
          <h2 className="mb-3 font-semibold">Tus puntuaciones ({minutes} min)</h2>
          <div className="h-56">
            <ResponsiveContainer>
              <LineChart data={runs} margin={{ left: -20, right: 8, top: 8 }}>
                <CartesianGrid stroke="rgb(var(--line))" strokeDasharray="3 3" />
                <XAxis dataKey="n" stroke="rgb(var(--muted))" fontSize={12} />
                <YAxis stroke="rgb(var(--muted))" fontSize={12} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ background: "rgb(var(--panel))", border: "1px solid rgb(var(--line))", borderRadius: 12 }}
                  labelFormatter={(n) => `Intento ${n}`}
                />
                <Line type="monotone" dataKey="score" name="Puntos" stroke="rgb(var(--rush))" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}
    </div>
  );
}

function RushRun({
  puzzles,
  minutes,
  onFinish,
}: {
  puzzles: Puzzle[];
  minutes: number;
  onFinish: (score: number, attempts: Attempt[]) => void;
}) {
  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [strikes, setStrikes] = useState(0);
  const [left, setLeft] = useState(minutes * 60_000);
  const attempts = useRef<Attempt[]>([]);
  const ended = useRef(false);
  const scoreRef = useRef(0);
  useActivity("tactics", "rush");

  const end = useCallback(() => {
    if (ended.current) return;
    ended.current = true;
    onFinish(scoreRef.current, attempts.current);
  }, [onFinish]);

  useEffect(() => {
    const deadline = performance.now() + minutes * 60_000;
    const id = window.setInterval(() => {
      const ms = deadline - performance.now();
      setLeft(ms);
      if (ms <= 0) end();
    }, 100);
    return () => window.clearInterval(id);
  }, [end, minutes]);

  const puzzle = puzzles[index] ?? null;
  const p = usePuzzle(puzzle, {
    onDone: (solved, seconds) => {
      if (!puzzle || ended.current) return;
      attempts.current.push({ puzzle_id: puzzle.id, solved, seconds });
      if (solved) {
        scoreRef.current += 1;
        setScore(scoreRef.current);
      } else {
        const s = strikes + 1;
        setStrikes(s);
        if (s >= MAX_STRIKES) {
          window.setTimeout(end, 500);
          return;
        }
      }
      window.setTimeout(() => {
        if (index + 1 >= puzzles.length) end();
        else setIndex(index + 1);
      }, solved ? 250 : 500);
    },
  });

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
      <div className="mx-auto w-full max-w-[min(100%,calc(100vh-8rem))]">
        <div className={`relative rounded-md ${p.flash === "bad" ? "flash-bad animate-shake" : ""} ${p.flash === "good" ? "flash-good" : ""}`}>
          <Board
            fen={p.fen}
            orientation={p.color}
            movable={p.status === "play" && p.turn === p.color ? p.color : undefined}
            dests={p.dests}
            lastMove={p.lastMove}
            check={p.check}
            onMove={(f, t) => p.userMove(f, t)}
          />
          {p.promo && (
            <Promotion
              color={p.color}
              onPick={(role) => {
                const m = p.promo!;
                p.setPromo(null);
                p.userMove(m.from, m.to, role);
              }}
              onCancel={p.resetPromo}
            />
          )}
        </div>
      </div>
      <aside className="space-y-4">
        <div className="card text-center">
          <div className={`font-mono text-5xl font-extrabold tabular-nums ${left < 20_000 ? "text-bad" : ""}`}>
            {formatClock(left)}
          </div>
          <div className="mt-3 text-sm text-muted">Puntos</div>
          <div className="text-6xl font-extrabold text-rush">{score}</div>
          <div className="mt-3 flex justify-center gap-2 text-2xl">
            {Array.from({ length: MAX_STRIKES }, (_, i) => (
              <span key={i} className={i < strikes ? "text-bad" : "text-line"}>
                ✗
              </span>
            ))}
          </div>
          <div className="mt-3 text-sm text-muted">
            Juegan las {p.color === "white" ? "blancas" : "negras"} · puzzle {puzzle?.rating}
          </div>
        </div>
        <button className="btn-ghost w-full" onClick={end}>
          Terminar
        </button>
      </aside>
    </div>
  );
}
