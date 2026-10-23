import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Board from "../components/Board";
import Promotion from "../components/Promotion";
import { api } from "../lib/api";
import { THEME_FILTERS, puzzleGoal, themeLabel } from "../lib/labels";
import { prefs } from "../lib/prefs";
import type { Puzzle } from "../lib/types";
import { usePuzzle } from "../lib/usePuzzle";
import { useActivity } from "../lib/useActivity";

interface AttemptResult {
  rating_before: number;
  rating_after: number;
}

export default function Puzzles() {
  const [params, setParams] = useSearchParams();
  const theme = params.get("theme");
  const area = params.get("area") === "endgames" ? "endgames" : "tactics";
  const review = params.get("review") === "1";
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null);
  const [error, setError] = useState("");
  const [rating, setRating] = useState<number | null>(null);
  const [lastDelta, setLastDelta] = useState<number | null>(null);
  const [showGoal, setShowGoal] = useState(prefs.puzzleGoal);
  const [showHint, setShowHint] = useState(false);
  const [session, setSession] = useState({ solved: 0, failed: 0 });
  const [dueCount, setDueCount] = useState(0);
  useActivity(area, review ? "review" : "puzzles");

  const load = useCallback(() => {
    setError("");
    setShowHint(false);
    const q = new URLSearchParams();
    if (theme) q.set("theme", theme);
    if (review) q.set("review", "true");
    q.set("area", area);
    api<Puzzle>(`/puzzles/next?${q}`)
      .then(setPuzzle)
      .catch((e) => {
        setPuzzle(null);
        setError(e.message);
      });
    api<{ due: number }>("/puzzles/review/count").then((r) => setDueCount(r.due)).catch(() => undefined);
  }, [area, review, theme]);

  useEffect(load, [load]);

  // Tu ELO actual, visible siempre (no solo al terminar un puzzle)
  useEffect(() => {
    setLastDelta(null);
    api<{ ratings: Record<string, { rating: number }> }>("/stats/overview")
      .then((o) => setRating(o.ratings[area].rating))
      .catch(() => undefined);
  }, [area]);

  const p = usePuzzle(puzzle, {
    onDone: (solved, seconds) => {
      if (!puzzle) return;
      setSession((s) => (solved ? { ...s, solved: s.solved + 1 } : { ...s, failed: s.failed + 1 }));
      api<AttemptResult>(`/puzzles/${puzzle.id}/attempt`, {
        body: { solved, seconds, mode: puzzle.review ? "review" : "normal", area },
      })
        .then((r) => {
          setRating(r.rating_after);
          // Los repasos no mueven el ELO: se conserva el último cambio real
          if (!puzzle.review) setLastDelta(r.rating_after - r.rating_before);
        })
        .catch(() => undefined);
    },
  });

  const done = p.status === "solved" || p.status === "failed";

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Enter" && done) load();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [done, load]);

  function setFilter(next: { theme?: string | null; review?: boolean }) {
    const q = new URLSearchParams();
    if (area === "endgames") q.set("area", "endgames");
    if (next.review) q.set("review", "1");
    else if (next.theme) q.set("theme", next.theme);
    setParams(q);
  }

  const title = area === "endgames" ? "Finales" : review ? "Repaso de fallos" : "Puzzles";
  const score = (
    <span className="text-sm text-muted">
      <span className="text-good">{session.solved} ✓</span> · <span className="text-bad">{session.failed} ✗</span>
    </span>
  );
  const elo = (
    <span className="text-lg font-extrabold">
      {rating ?? "–"}
      {lastDelta !== null && (
        <span className={`ml-1.5 text-sm ${lastDelta > 0 ? "text-good" : lastDelta < 0 ? "text-bad" : "text-muted"}`}>
          {lastDelta > 0 ? `+${lastDelta}` : lastDelta === 0 ? "±0" : lastDelta}
        </span>
      )}
    </span>
  );

  return (
    <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_320px] lg:gap-6">
      {/* Móvil: título, marcador y ELO encima del tablero; así el tablero queda centrado y los botones debajo */}
      <header className="flex items-center justify-between gap-3 lg:hidden">
        <div>
          <h1 className="text-xl font-extrabold">{title}</h1>
          {score}
        </div>
        <div className="text-right">
          <div className="text-xs text-muted">ELO de {area === "endgames" ? "finales" : "táctica"}</div>
          {elo}
        </div>
      </header>

      <div className="mx-auto w-full max-w-[min(100%,calc(100vh-8rem))]">
        <div
          className={`relative rounded-md ${p.flash === "bad" ? "flash-bad animate-shake" : ""} ${
            p.flash === "good" ? "flash-good" : ""
          }`}
        >
          <Board
            fen={p.fen}
            orientation={p.color}
            movable={p.status === "play" && p.turn === p.color ? p.color : undefined}
            dests={p.dests}
            lastMove={p.lastMove}
            check={p.check}
            shapes={showHint && p.hint ? [{ orig: p.hint, brush: "green" }] : undefined}
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

      <aside className="space-y-4" data-panel="puzzle">
        <div className="card flex flex-col gap-3">
          <div className="hidden items-center justify-between lg:flex">
            <h2 className="text-xl font-extrabold">{title}</h2>
            {score}
          </div>

          <div className="hidden items-center justify-between rounded-xl border border-line px-3 py-2 text-sm lg:flex">
            <span className="text-muted">Tu ELO de {area === "endgames" ? "finales" : "táctica"}</span>
            {elo}
          </div>

          {error && <p className="text-sm text-bad">{error}</p>}

          {puzzle && (
            <>
              <div
                className={`rounded-xl p-3 font-semibold ${
                  p.status === "solved"
                    ? "bg-good/15 text-good"
                    : p.status === "failed"
                      ? "bg-bad/15 text-bad"
                      : "bg-panel2"
                }`}
              >
                {p.status === "intro" && "Mira la jugada del rival…"}
                {p.status === "play" &&
                  (p.wrong ? (
                    "No es eso. Sigue intentándolo."
                  ) : showHint ? (
                    <>
                      Mueve la pieza marcada
                      <span className="block text-sm font-normal text-muted">Con pista, el puzzle cuenta como fallado</span>
                    </>
                  ) : (
                    <>
                      Juegan las {p.color === "white" ? "blancas" : "negras"}
                      <span className="block text-sm font-normal text-muted">
                        {showGoal ? puzzleGoal(puzzle.themes) : "Encuentra la mejor jugada"}
                      </span>
                    </>
                  ))}
                {p.status === "solved" && "¡Correcto!"}
                {p.status === "failed" &&
                  (p.recovered
                    ? `${showHint && !p.wrong ? "¡Resuelto con pista!" : "¡Bien, ahora sí!"} Cuenta como fallado y volverá a tu cola de repaso.`
                    : "Puzzle fallado. Volverá a tu cola de repaso.")}
              </div>


              {done ? (
                <>
                  <div className="text-sm text-muted">
                    Puzzle {puzzle.rating} ·{" "}
                    <a className="underline" href={`https://lichess.org/training/${puzzle.id}`} target="_blank" rel="noreferrer">
                      Lichess #{puzzle.id}
                    </a>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {puzzle.themes.map((t) => (
                      <span key={t} className="rounded-full bg-panel2 px-2 py-0.5 text-xs">
                        {themeLabel(t)}
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    {p.status === "failed" && (
                      <button
                        className="btn-ghost flex-1"
                        onClick={() => {
                          setShowHint(false);
                          p.retry();
                        }}
                      >
                        Reintentar
                      </button>
                    )}
                    <button className="btn-primary flex-1" onClick={load}>
                      Siguiente ↵
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex gap-2">
                  <button
                    className="btn-ghost flex-1"
                    disabled={p.status !== "play"}
                    onClick={() => {
                      setShowHint(true);
                      p.takeHint();
                    }}
                  >
                    Pista
                  </button>
                  <button className="btn-ghost flex-1" disabled={p.status !== "play"} onClick={p.showSolution}>
                    Ver solución
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        <label className="card flex cursor-pointer items-center justify-between gap-3 text-sm">
          <span>
            <span className="font-semibold">Mostrar el objetivo</span>
            <span className="block text-muted">«Mate en 2», «Gana material»… Es una pista: Lichess no lo enseña.</span>
          </span>
          <input
            type="checkbox"
            className="h-5 w-5"
            checked={showGoal}
            onChange={(e) => {
              prefs.puzzleGoal = e.target.checked;
              setShowGoal(e.target.checked);
            }}
          />
        </label>

        <div className="card space-y-2">
          <div className="text-sm font-semibold text-muted">Entrenar un tema</div>
          <div className="flex flex-wrap gap-1.5">
            <button className={`chip ${!theme && !review ? "chip-on" : ""}`} onClick={() => setFilter({})}>
              Mezcla
            </button>
            <button className={`chip ${review ? "chip-on" : ""}`} onClick={() => setFilter({ review: true })}>
              Repaso de fallos{dueCount ? ` (${dueCount})` : ""}
            </button>
            {THEME_FILTERS.map((t) => (
              <button key={t} className={`chip ${theme === t ? "chip-on" : ""}`} onClick={() => setFilter({ theme: t })}>
                {themeLabel(t)}
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
