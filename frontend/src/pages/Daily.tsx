import { useEffect, useMemo, useState } from "react";
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
}

type Kind = "puzzle" | "own-game";

export default function Daily() {
  const [data, setData] = useState<DailyData | null>(null);
  const [open, setOpen] = useState<Kind | null>(null);
  useActivity("tactics", "daily");

  const load = () => api<DailyData>("/daily").then(setData);
  useEffect(() => {
    load();
  }, []);

  function complete(kind: Kind, success: boolean) {
    api(`/daily/${kind}`, { body: { success } }).then(load);
  }

  if (!data) return <p className="text-muted">Cargando desafíos…</p>;

  const cards: { kind: Kind; title: string; text: string; available: boolean }[] = [
    { kind: "puzzle", title: "Puzzle del día", text: "El mismo para toda la casa. Un intento.", available: !!data.puzzle },
    {
      kind: "own-game",
      title: "Encuentra la mejor jugada",
      text: data.own ? "Una posición de tus partidas donde te equivocaste." : "Juega o importa partidas analizadas para desbloquearlo.",
      available: !!data.own,
    },
  ];
  const available = cards.filter((c) => c.available);
  const doneCount = available.filter((c) => data.done[c.kind]).length;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-extrabold">Desafíos del día</h1>
          <p className="text-muted">Retos cortos que mantienen tu racha aunque hoy tengas poco tiempo.</p>
        </div>
        <div className="card px-4 py-2 text-center">
          <div className="text-2xl font-extrabold">
            {doneCount}/{available.length}
          </div>
          <div className="text-xs text-muted">hechos hoy</div>
        </div>
      </header>

      <div className="grid gap-3 md:grid-cols-2">
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

const OWN_TRIES = 3;

function OwnGame({ own, done, onDone }: { own: Own; done?: { success: boolean }; onDone: (ok: boolean) => void }) {
  const chess = useMemo(() => new Chess(own.fen), [own.fen]);
  const [fen, setFen] = useState(own.fen);
  const [result, setResult] = useState<boolean | null>(null);
  const [tried, setTried] = useState<string[]>([]); // jugadas equivocadas (SAN)
  const [shake, setShake] = useState(false);
  const [note, setNote] = useState("");
  const [shapes, setShapes] = useState<DrawShape[]>([]);
  const left = OWN_TRIES - tried.length;

  function finish(ok: boolean) {
    setResult(ok);
    if (!ok) {
      const [orig, dest] = uciToKeys(own.best_uci);
      setShapes([{ orig, dest, brush: "green" }]);
      setFen(own.fen);
    }
    if (!done) onDone(ok);
  }

  function onMove(from: Key, to: Key) {
    if (result !== null) return;
    const c = new Chess(own.fen);
    let san: string;
    try {
      san = c.move({ from, to, promotion: own.best_uci[4] ?? "q" }).san;
    } catch {
      return;
    }
    if (`${from}${to}` === own.best_uci.slice(0, 4)) {
      setFen(c.fen());
      sound.good();
      confetti({ particleCount: 60, spread: 60, origin: { y: 0.6 }, disableForReducedMotion: true });
      finish(true);
      return;
    }
    // Fallo: la pieza vuelve a su sitio y, si quedan intentos, se puede probar otra jugada
    setFen(own.fen);
    sound.bad();
    setShake(true);
    window.setTimeout(() => setShake(false), 400);
    if (tried.includes(san)) {
      setNote(`Ya probaste ${san}. Busca otra jugada.`);
      return;
    }
    const next = [...tried, san];
    setTried(next);
    setNote(san === own.played_san ? `${san} es lo que jugaste en la partida: precisamente el error.` : `${san} no es la mejor.`);
    if (next.length >= OWN_TRIES) finish(false);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className={`mx-auto w-full max-w-[min(100%,calc(100vh-14rem))] rounded-md ${shake ? "flash-bad animate-shake" : ""} ${result ? "flash-good" : ""}`}>
        <Board
          fen={fen}
          orientation={own.user_color}
          movable={result === null ? own.user_color : undefined}
          dests={toDests(chess)}
          shapes={shapes}
          onMove={onMove}
        />
      </div>
      <aside className="card h-fit space-y-3">
        <h2 className="font-bold">Encuentra la mejor jugada</h2>
        <p className="text-sm text-muted">
          En esta posición de una de tus partidas jugaste {own.played_san} ({CLASS_LABEL[own.classification]?.toLowerCase()}). ¿Qué era mejor?
        </p>
        {result === null && (
          <>
            <div className="flex items-center gap-1.5 text-sm">
              <span className="text-muted">Intentos:</span>
              {Array.from({ length: OWN_TRIES }, (_, i) => (
                <span key={i} className={`h-2.5 w-2.5 rounded-full ${i < tried.length ? "bg-bad" : "bg-line"}`} />
              ))}
              <span className="text-muted">
                · te queda{left === 1 ? "" : "n"} {left}
              </span>
            </div>
            {note && <p className="text-sm font-semibold text-bad">{note}</p>}
            <button className="btn-ghost w-full" onClick={() => finish(false)}>
              Ver solución
            </button>
          </>
        )}
        {result === true && (
          <p className="font-semibold text-good">
            ¡Exacto! {own.best_san} era lo mejor{tried.length ? ` (al ${tried.length + 1}.º intento)` : ""}.
          </p>
        )}
        {result === false && <p className="font-semibold text-bad">Lo mejor era {own.best_san} (flecha verde).</p>}
        {tried.length > 0 && <p className="text-xs text-muted">Probaste: {tried.join(", ")}</p>}
        <Link className="text-sm underline" to={`/revision/${own.game_id}`}>
          Ver la partida
        </Link>
      </aside>
    </div>
  );
}
