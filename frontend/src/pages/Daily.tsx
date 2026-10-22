import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Chess } from "chess.js";
import confetti from "canvas-confetti";
import Board, { toDests, uciToKeys, type Color, type DrawShape, type Key } from "../components/Board";
import Promotion from "../components/Promotion";
import { api } from "../lib/api";
import { CLASS_LABEL } from "../lib/labels";
import { sound } from "../lib/sound";
import type { Puzzle } from "../lib/types";
import { usePuzzle } from "../lib/usePuzzle";
import { useActivity } from "../lib/useActivity";

interface Own {
  game_id: number;
  ply: number;
  fen: string;
  best_uci: string;
  best_san: string;
  played_san: string;
  user_color: Color;
  classification: string;
}

interface DailyData {
  day: string;
  puzzle: Puzzle | null;
  own: Own | null;
  done: Record<string, { success: boolean; score: number }>;
  best_visual: number;
}

type Kind = "puzzle" | "own-game" | "visual";

export default function Daily() {
  const [data, setData] = useState<DailyData | null>(null);
  const [open, setOpen] = useState<Kind | null>(null);
  useActivity("tactics", "daily");

  const load = () => api<DailyData>("/daily").then(setData);
  useEffect(() => {
    load();
  }, []);

  function complete(kind: Kind, success: boolean, score = 0) {
    api(`/daily/${kind}`, { body: { success, score } }).then(load);
  }

  if (!data) return <p className="text-muted">Cargando desafíos…</p>;
  const doneCount = Object.keys(data.done).length;

  const cards: { kind: Kind; title: string; text: string; available: boolean }[] = [
    { kind: "puzzle", title: "Puzzle del día", text: "El mismo para toda la casa. Un intento.", available: !!data.puzzle },
    {
      kind: "own-game",
      title: "Encuentra la mejor jugada",
      text: data.own ? "Una posición de tus partidas donde te equivocaste." : "Juega o importa partidas analizadas para desbloquearlo.",
      available: !!data.own,
    },
    { kind: "visual", title: "Visualización: coordenadas", text: `30 segundos para encontrar casillas. Récord: ${data.best_visual}.`, available: true },
  ];

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-extrabold">Desafíos del día</h1>
          <p className="text-muted">Retos cortos que mantienen tu racha aunque hoy tengas poco tiempo.</p>
        </div>
        <div className="card px-4 py-2 text-center">
          <div className="text-2xl font-extrabold">{doneCount}/3</div>
          <div className="text-xs text-muted">hechos hoy</div>
        </div>
      </header>

      <div className="grid gap-3 md:grid-cols-3">
        {cards.map((c) => {
          const d = data.done[c.kind];
          return (
            <button
              key={c.kind}
              disabled={!c.available}
              onClick={() => setOpen(c.kind)}
              className={`card text-left transition hover:bg-panel2 disabled:opacity-50 ${open === c.kind ? "ring-2 ring-fg/30" : ""}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="font-semibold">{c.title}</div>
                {d && <span className={d.success ? "text-good" : "text-bad"}>{d.success ? "✓" : "✗"}</span>}
              </div>
              <div className="mt-1 text-sm text-muted">{c.text}</div>
            </button>
          );
        })}
      </div>

      {open === "puzzle" && data.puzzle && (
        <DailyPuzzle puzzle={data.puzzle} done={data.done.puzzle} onDone={(ok) => complete("puzzle", ok)} />
      )}
      {open === "own-game" && data.own && (
        <OwnGame own={data.own} done={data.done["own-game"]} onDone={(ok) => complete("own-game", ok)} />
      )}
      {open === "visual" && <Coordinates onDone={(score) => complete("visual", score >= 10, score)} best={data.best_visual} />}
    </div>
  );
}

function DailyPuzzle({ puzzle, done, onDone }: { puzzle: Puzzle; done?: { success: boolean }; onDone: (ok: boolean) => void }) {
  const p = usePuzzle(puzzle, { onDone: (ok) => !done && onDone(ok) });
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className={`relative mx-auto w-full max-w-[min(100%,calc(100vh-14rem))] rounded-md ${p.flash === "bad" ? "flash-bad animate-shake" : ""} ${p.flash === "good" ? "flash-good" : ""}`}>
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
          <Promotion color={p.color} onPick={(r) => { const m = p.promo!; p.setPromo(null); p.userMove(m.from, m.to, r); }} onCancel={p.resetPromo} />
        )}
      </div>
      <aside className="card h-fit space-y-2">
        <h2 className="font-bold">Puzzle del día</h2>
        <p className="text-sm text-muted">
          {done ? (done.success ? "Ya lo resolviste hoy ✓ (puedes repetirlo)." : "Hoy no salió. Mañana, otro.") : `Juegan las ${p.color === "white" ? "blancas" : "negras"}.`}
        </p>
        {p.status === "solved" && <p className="font-semibold text-good">¡Correcto!</p>}
        {p.status === "failed" && <p className="font-semibold text-bad">Fallado.</p>}
        {p.status === "play" && (
          <button className="btn-ghost w-full" onClick={p.showSolution}>
            Ver solución
          </button>
        )}
        <p className="text-xs text-muted">Puzzle {puzzle.rating} · Lichess #{puzzle.id}</p>
      </aside>
    </div>
  );
}

function OwnGame({ own, done, onDone }: { own: Own; done?: { success: boolean }; onDone: (ok: boolean) => void }) {
  const chess = useMemo(() => new Chess(own.fen), [own.fen]);
  const [fen, setFen] = useState(own.fen);
  const [result, setResult] = useState<boolean | null>(null);
  const [shapes, setShapes] = useState<DrawShape[]>([]);

  function onMove(from: Key, to: Key) {
    if (result !== null) return;
    const ok = `${from}${to}` === own.best_uci.slice(0, 4);
    const c = new Chess(own.fen);
    try {
      c.move({ from, to, promotion: own.best_uci[4] ?? "q" });
      setFen(c.fen());
    } catch {
      return;
    }
    setResult(ok);
    if (ok) {
      sound.good();
      confetti({ particleCount: 60, spread: 60, origin: { y: 0.6 }, disableForReducedMotion: true });
    } else {
      sound.bad();
      const [orig, dest] = uciToKeys(own.best_uci);
      setShapes([{ orig, dest, brush: "green" }]);
      setFen(own.fen);
    }
    if (!done) onDone(ok);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className={`mx-auto w-full max-w-[min(100%,calc(100vh-14rem))] rounded-md ${result === false ? "flash-bad animate-shake" : ""} ${result ? "flash-good" : ""}`}>
        <Board
          fen={fen}
          orientation={own.user_color}
          movable={result === null ? own.user_color : undefined}
          dests={toDests(chess)}
          shapes={shapes}
          onMove={onMove}
        />
      </div>
      <aside className="card h-fit space-y-2">
        <h2 className="font-bold">Encuentra la mejor jugada</h2>
        <p className="text-sm text-muted">
          En esta posición de una de tus partidas jugaste {own.played_san} ({CLASS_LABEL[own.classification]?.toLowerCase()}). ¿Qué era mejor?
        </p>
        {result === true && <p className="font-semibold text-good">¡Exacto! {own.best_san} era lo mejor.</p>}
        {result === false && <p className="font-semibold text-bad">No. Lo mejor era {own.best_san}.</p>}
        <Link className="text-sm underline" to={`/revision/${own.game_id}`}>
          Ver la partida
        </Link>
      </aside>
    </div>
  );
}

const FILES = "abcdefgh";

function Coordinates({ onDone, best }: { onDone: (score: number) => void; best: number }) {
  const [running, setRunning] = useState(false);
  const [orientation, setOrientation] = useState<Color>("white");
  const [target, setTarget] = useState("e4");
  const [score, setScore] = useState(0);
  const [left, setLeft] = useState(30_000);
  const [flash, setFlash] = useState<{ sq: string; ok: boolean } | null>(null);
  const [last, setLast] = useState<number | null>(null);
  const scoreRef = useRef(0);

  const randomSquare = () => `${FILES[Math.floor(Math.random() * 8)]}${1 + Math.floor(Math.random() * 8)}`;

  function start() {
    setOrientation(Math.random() < 0.5 ? "white" : "black");
    scoreRef.current = 0;
    setScore(0);
    setTarget(randomSquare());
    setLeft(30_000);
    setLast(null);
    setRunning(true);
  }

  useEffect(() => {
    if (!running) return;
    const end = performance.now() + 30_000;
    const id = window.setInterval(() => {
      const ms = end - performance.now();
      setLeft(Math.max(0, ms));
      if (ms <= 0) {
        window.clearInterval(id);
        setRunning(false);
        setLast(scoreRef.current);
        onDone(scoreRef.current);
        if (scoreRef.current > best) confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 }, disableForReducedMotion: true });
      }
    }, 100);
    return () => window.clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running]);

  function click(sq: string) {
    if (!running) return;
    const ok = sq === target;
    setFlash({ sq, ok });
    window.setTimeout(() => setFlash(null), 250);
    if (ok) {
      scoreRef.current += 1;
      setScore(scoreRef.current);
      setTarget(randomSquare());
    } else sound.bad();
  }

  const ranks = orientation === "white" ? [8, 7, 6, 5, 4, 3, 2, 1] : [1, 2, 3, 4, 5, 6, 7, 8];
  const files = orientation === "white" ? FILES.split("") : FILES.split("").reverse();

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className="relative mx-auto aspect-square w-full max-w-[min(100%,calc(100vh-14rem))]">
        <div className="grid h-full w-full grid-cols-8 overflow-hidden rounded-md">
          {ranks.map((r) =>
            files.map((f) => {
              const sq = `${f}${r}`;
              const light = (FILES.indexOf(f) + r) % 2 === 1;
              const fl = flash?.sq === sq ? (flash.ok ? "bg-good" : "bg-bad") : light ? "bg-[#f0d9b5]" : "bg-[#b58863]";
              return <button key={sq} aria-label={sq} className={`${fl} transition-colors`} onClick={() => click(sq)} />;
            }),
          )}
        </div>
        {running && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <span className="rounded-2xl bg-black/60 px-6 py-2 text-6xl font-extrabold text-white">{target}</span>
          </div>
        )}
      </div>
      <aside className="card h-fit space-y-3">
        <h2 className="font-bold">Visualización: coordenadas</h2>
        <p className="text-sm text-muted">
          Haz clic en la casilla que aparece. El tablero puede salir desde el lado de las negras. 10 aciertos completan el reto.
        </p>
        <div className="flex justify-between text-2xl font-extrabold tabular-nums">
          <span>{score}</span>
          <span className={left < 5000 ? "text-bad" : ""}>{(left / 1000).toFixed(1)}s</span>
        </div>
        {last !== null && <p className={last >= 10 ? "font-semibold text-good" : "text-muted"}>Has hecho {last}. Récord: {Math.max(best, last)}.</p>}
        <button className="btn-primary w-full" onClick={start} disabled={running}>
          {last === null ? "Empezar" : "Otra vez"}
        </button>
      </aside>
    </div>
  );
}
