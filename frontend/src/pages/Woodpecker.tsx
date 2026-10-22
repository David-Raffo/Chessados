import { useCallback, useEffect, useState } from "react";
import confetti from "canvas-confetti";
import Board from "../components/Board";
import Promotion from "../components/Promotion";
import { api } from "../lib/api";
import { formatDuration } from "../lib/labels";
import type { Puzzle } from "../lib/types";
import { usePuzzle } from "../lib/usePuzzle";
import { useActivity } from "../lib/useActivity";

interface Cycle {
  number: number;
  position: number;
  solved: number;
  accuracy: number | null;
  seconds: number;
  target_days: number;
  started_at: string;
  finished_at: string | null;
  days: number;
}

interface WSet {
  id: number;
  size: number;
  cycles: Cycle[];
  finished_cycle?: number | null;
}

type WPuzzle = Puzzle & { cycle: number; index: number; size: number };

export default function Woodpecker() {
  const [set, setSet] = useState<WSet | null | undefined>(undefined);
  const [solving, setSolving] = useState(false);

  const load = useCallback(() => {
    api<WSet | null>("/woodpecker").then(setSet);
  }, []);
  useEffect(load, [load]);

  if (set === undefined) return <p className="text-muted">Cargando…</p>;
  if (solving && set) return <Solve onExit={() => { setSolving(false); load(); }} />;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-extrabold">Método Woodpecker</h1>
        <p className="text-muted">
          Un bloque fijo de puzzles que repites en ciclos cada vez más rápidos para fijar los patrones. Es un modo
          opcional: hay entrenadores que dudan de que repetir sea lo que funciona, así que úsalo cuando tu ELO de
          táctica se estanque.
        </p>
      </header>
      {set ? <SetView set={set} onSolve={() => setSolving(true)} onReset={load} /> : <Create onCreated={setSet} />}
    </div>
  );
}

function Create({ onCreated }: { onCreated: (s: WSet) => void }) {
  const [size, setSize] = useState(100);
  const [busy, setBusy] = useState(false);
  return (
    <section className="card space-y-4">
      <h2 className="font-bold">Crea tu bloque</h2>
      <p className="text-sm text-muted">
        Elegiré puzzles algo por debajo de tu nivel de táctica. El primer ciclo, a tu ritmo (unos 25 al día); cada
        ciclo siguiente, en la mitad de días.
      </p>
      <div className="grid grid-cols-3 gap-2">
        {[100, 200, 300].map((n) => (
          <button
            key={n}
            className={`rounded-xl border p-3 text-center ${size === n ? "border-tactics bg-tactics/10" : "border-line"}`}
            onClick={() => setSize(n)}
          >
            <div className="text-2xl font-extrabold">{n}</div>
            <div className="text-xs text-muted">puzzles</div>
          </button>
        ))}
      </div>
      <button
        className="btn-primary w-full"
        disabled={busy}
        onClick={() => {
          setBusy(true);
          api<WSet>("/woodpecker", { body: { size } }).then(onCreated).finally(() => setBusy(false));
        }}
      >
        Crear bloque de {size}
      </button>
    </section>
  );
}

function SetView({ set, onSolve, onReset }: { set: WSet; onSolve: () => void; onReset: () => void }) {
  const current = set.cycles[set.cycles.length - 1];
  const pct = Math.round((100 * current.position) / set.size);
  return (
    <>
      <section className="card space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <div className="text-sm text-muted">Ciclo {current.number}</div>
            <div className="text-3xl font-extrabold">
              {current.position} / {set.size}
            </div>
          </div>
          <div className="text-right text-sm text-muted">
            Objetivo: {current.target_days} día{current.target_days > 1 ? "s" : ""}
            <br />
            Día {current.days}
          </div>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-panel2">
          <div className="h-full bg-tactics transition-all" style={{ width: `${pct}%` }} />
        </div>
        <button className="btn-primary w-full py-3 text-lg" onClick={onSolve}>
          {current.position ? "Continuar ciclo" : `Empezar ciclo ${current.number}`}
        </button>
      </section>

      <section className="card p-0">
        <table className="w-full text-sm">
          <thead className="text-left text-muted">
            <tr>
              <th className="p-3">Ciclo</th>
              <th className="p-3">Progreso</th>
              <th className="p-3">Acierto</th>
              <th className="p-3">Tiempo</th>
              <th className="p-3">Días</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {set.cycles.map((c) => (
              <tr key={c.number}>
                <td className="p-3 font-semibold">{c.number}</td>
                <td className="p-3">{c.finished_at ? "✓ Terminado" : `${c.position}/${set.size}`}</td>
                <td className="p-3">{c.accuracy != null ? `${c.accuracy}%` : "—"}</td>
                <td className="p-3">{c.seconds ? formatDuration(c.seconds) : "—"}</td>
                <td className={`p-3 ${c.finished_at && c.days > c.target_days ? "text-bad" : ""}`}>
                  {c.days} / {c.target_days}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <button
        className="btn-ghost text-sm text-bad"
        onClick={() => {
          if (window.confirm("¿Abandonar este bloque? Podrás crear otro nuevo.")) api("/woodpecker", { method: "DELETE" }).then(onReset);
        }}
      >
        Abandonar el bloque
      </button>
    </>
  );
}

function Solve({ onExit }: { onExit: () => void }) {
  const [puzzle, setPuzzle] = useState<WPuzzle | null>(null);
  const [stats, setStats] = useState({ solved: 0, failed: 0 });
  const [finished, setFinished] = useState<number | null>(null);
  useActivity("tactics", "woodpecker");

  const load = useCallback(() => {
    api<WPuzzle>("/woodpecker/next").then(setPuzzle);
  }, []);
  useEffect(load, [load]);

  const p = usePuzzle(puzzle, {
    onDone: (solved, seconds) => {
      if (!puzzle) return;
      setStats((s) => (solved ? { ...s, solved: s.solved + 1 } : { ...s, failed: s.failed + 1 }));
      api<WSet>("/woodpecker/attempt", { body: { puzzle_id: puzzle.id, solved, seconds } }).then((r) => {
        if (r.finished_cycle) {
          setFinished(r.finished_cycle);
          confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 }, disableForReducedMotion: true });
        } else if (solved) {
          window.setTimeout(load, 400);
        }
      });
    },
  });

  if (finished) {
    return (
      <div className="card mx-auto max-w-md space-y-3 text-center">
        <div className="text-5xl">🏁</div>
        <h2 className="text-2xl font-extrabold">¡Ciclo {finished} terminado!</h2>
        <p className="text-muted">Descansa un día y empieza el siguiente ciclo: mismo bloque, la mitad de días.</p>
        <button className="btn-primary w-full" onClick={onExit}>
          Ver mis ciclos
        </button>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
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
        <div className="card space-y-3">
          <div className="flex justify-between">
            <h2 className="font-bold">Ciclo {puzzle?.cycle}</h2>
            <span className="text-sm">
              <span className="text-good">{stats.solved} ✓</span> · <span className="text-bad">{stats.failed} ✗</span>
            </span>
          </div>
          <div className="text-3xl font-extrabold">
            {puzzle ? puzzle.index + 1 : "–"} <span className="text-lg text-muted">/ {puzzle?.size}</span>
          </div>
          <p className="text-sm text-muted">
            {p.status === "play" && (p.mistake ? "Fallado: termina el puzzle o pasa al siguiente." : `Juegan las ${p.color === "white" ? "blancas" : "negras"}`)}
            {p.status === "solved" && "¡Correcto!"}
            {p.status === "failed" && "Fallado. Volverá en el próximo ciclo."}
          </p>
          {(p.status === "failed" || (p.status === "play" && p.mistake)) && (
            <button className="btn-primary w-full" onClick={load}>
              Siguiente
            </button>
          )}
          {p.status === "play" && !p.mistake && (
            <button className="btn-ghost w-full" onClick={p.showSolution}>
              Ver solución
            </button>
          )}
        </div>
        <button className="btn-ghost w-full" onClick={onExit}>
          Pausar
        </button>
      </aside>
    </div>
  );
}
