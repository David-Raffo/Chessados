import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Chess } from "chess.js";
import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Board, { uciToKeys, type Color, type DrawShape, type Key } from "../components/Board";
import { api } from "../lib/api";
import { CLASS_LABEL, CLASS_SYMBOL, CLASS_TEXT, PHASE_LABEL, opponentName } from "../lib/labels";
import type { Game, MoveAnalysis } from "../lib/types";
import { useActivity } from "../lib/useActivity";

interface Position {
  fen: string;
  san?: string;
  lastMove?: Key[];
}

function parsePositions(pgn: string): Position[] {
  const c = new Chess();
  try {
    c.loadPgn(pgn);
  } catch {
    return [{ fen: c.fen() }];
  }
  const moves = c.history({ verbose: true });
  const out: Position[] = [{ fen: moves[0]?.before ?? c.fen() }];
  for (const m of moves) out.push({ fen: m.after, san: m.san, lastMove: [m.from as Key, m.to as Key] });
  return out;
}

function evalText(a: MoveAnalysis): string {
  if (a.mate != null) return `#${a.mate}`;
  const v = a.eval_cp / 100;
  return `${v > 0 ? "+" : ""}${v.toFixed(1)}`;
}

interface OpeningInfo {
  opening: { eco: string; name: string } | null;
  deviation: { ply: number; type: "you" | "opponent" | "end"; san: string | null; expected: string[] | null } | null;
}

const winChance =(cp: number) => 1 / (1 + Math.exp(-0.00368208 * cp));

export default function Review() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [game, setGame] = useState<Game | null>(null);
  const [error, setError] = useState("");
  const [ply, setPly] = useState(0);
  const [notes, setNotes] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [orientation, setOrientation] = useState<Color>("white");
  const [opening, setOpening] = useState<OpeningInfo | null>(null);
  useActivity("play", "review", id);

  const load = useCallback(() => {
    api<Game>(`/games/${id}`)
      .then((g) => {
        setGame(g);
        setNotes((n) => n || g.user_notes || "");
        if (g.reviewed || g.user_notes) setRevealed(true);
      })
      .catch((e) => setError(e.message));
  }, [id]);

  useEffect(load, [load]);
  useEffect(() => {
    api<OpeningInfo[]>(`/openings/deviations?game_id=${id}`)
      .then((r) => setOpening(r[0] ?? null))
      .catch(() => undefined);
  }, [id]);
  useEffect(() => {
    if (game) setOrientation(game.user_color);
  }, [game?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Mientras el worker analiza, se consulta cada 3 s
  useEffect(() => {
    if (!game || (game.analysis_status !== "pending" && game.analysis_status !== "running")) return;
    const t = window.setTimeout(load, 3000);
    return () => window.clearTimeout(t);
  }, [game, load]);

  const positions = useMemo(() => (game ? parsePositions(game.pgn) : []), [game?.pgn]); // eslint-disable-line react-hooks/exhaustive-deps
  const analysis = game?.analysis ?? [];
  const ready = game?.analysis_status === "done" && analysis.length > 0;
  const showEngine = revealed && ready;
  const current = ply > 0 ? analysis[ply - 1] : undefined;

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === "TEXTAREA") return;
      if (e.key === "ArrowLeft") setPly((p) => Math.max(0, p - 1));
      if (e.key === "ArrowRight") setPly((p) => Math.min(positions.length - 1, p + 1));
      if (e.key === "ArrowUp") setPly(0);
      if (e.key === "ArrowDown") setPly(positions.length - 1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [positions.length]);

  const shapes = useMemo((): DrawShape[] => {
    if (!showEngine || !current?.best_uci) return [];
    if (current.classification === "best" || current.classification === "good") return [];
    const [orig, dest] = uciToKeys(current.best_uci);
    return [{ orig, dest, brush: "green" }];
  }, [current, showEngine]);

  const chartData = useMemo(
    () =>
      analysis.map((a) => ({
        ply: a.ply,
        eval: Math.max(-10, Math.min(10, a.eval_cp / 100)),
        label: `${Math.ceil(a.ply / 2)}${a.ply % 2 ? "." : "…"} ${a.san}`,
      })),
    [analysis],
  );

  const summary = useMemo(() => {
    const mine = analysis.filter((a) => a.is_user_move);
    const count = (c: string) => mine.filter((a) => a.classification === c).length;
    return { inaccuracy: count("inaccuracy"), mistake: count("mistake"), blunder: count("blunder") };
  }, [analysis]);

  async function saveNotes() {
    if (!game) return;
    const g = await api<Game>(`/games/${game.id}`, { method: "PATCH", body: { user_notes: notes || "—" } });
    setGame({ ...game, user_notes: g.user_notes });
    setRevealed(true);
  }

  async function markReviewed() {
    if (!game) return;
    await api(`/games/${game.id}`, { method: "PATCH", body: { reviewed: true, user_notes: notes || game.user_notes } });
    navigate("/partidas");
  }

  if (error) return <p className="text-bad">{error}</p>;
  if (!game) return <p className="text-muted">Cargando partida…</p>;

  const pos = positions[Math.min(ply, positions.length - 1)];
  const whiteName = game.user_color === "white" ? "Tú" : opponentName(game);
  const blackName = game.user_color === "black" ? "Tú" : opponentName(game);
  const evalCp = showEngine ? (current ? current.eval_cp : analysis[0] ? 20 : 0) : 0;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-extrabold">
              {whiteName} vs {blackName}
            </h1>
            <p className="text-sm text-muted">
              {opening?.opening?.name ? `${opening.opening.name} · ` : ""}
              {game.result} · {game.time_control ?? "—"}
              {game.opponent_elo ? ` · rival ${game.opponent_elo}` : ""}
            </p>
          </div>
          <button className="btn-ghost" onClick={() => setOrientation(orientation === "white" ? "black" : "white")}>
            Girar
          </button>
        </div>

        <div className="mx-auto flex w-full max-w-[min(100%,calc(100vh-12rem))] gap-2">
          {showEngine && (
            <div className="relative w-3 shrink-0 overflow-hidden rounded bg-neutral-800">
              <div
                className="absolute inset-x-0 bottom-0 bg-neutral-100 transition-all duration-300"
                style={{
                  height: `${100 * (orientation === "white" ? winChance(evalCp) : 1 - winChance(evalCp))}%`,
                }}
              />
            </div>
          )}
          <div className="min-w-0 flex-1">
            <Board fen={pos.fen} orientation={orientation} lastMove={pos.lastMove} shapes={shapes} />
          </div>
        </div>

        <div className="flex justify-center gap-2">
          {[
            ["⏮", () => setPly(0)],
            ["◀", () => setPly(Math.max(0, ply - 1))],
            ["▶", () => setPly(Math.min(positions.length - 1, ply + 1))],
            ["⏭", () => setPly(positions.length - 1)],
          ].map(([label, fn]) => (
            <button key={label as string} className="btn-ghost w-14" onClick={fn as () => void}>
              {label as string}
            </button>
          ))}
        </div>

        {showEngine && (
          <div className="card h-40 p-2">
            <ResponsiveContainer>
              <AreaChart
                data={chartData}
                margin={{ left: -28, right: 4, top: 4, bottom: 0 }}
                onClick={(e) => e?.activeLabel != null && setPly(Number(e.activeLabel))}
              >
                <defs>
                  <linearGradient id="evalFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="50%" stopColor="rgb(var(--fg))" stopOpacity={0.35} />
                    <stop offset="50%" stopColor="rgb(var(--fg))" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgb(var(--line))" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="ply" hide />
                <YAxis domain={[-10, 10]} ticks={[-5, 0, 5]} stroke="rgb(var(--muted))" fontSize={11} />
                <ReferenceLine y={0} stroke="rgb(var(--muted))" />
                {ply > 0 && <ReferenceLine x={ply} stroke="rgb(var(--play))" strokeWidth={2} />}
                <Tooltip
                  contentStyle={{ background: "rgb(var(--panel))", border: "1px solid rgb(var(--line))", borderRadius: 12 }}
                  labelFormatter={(_, p) => p?.[0]?.payload?.label ?? ""}
                  formatter={(v: number) => [v > 0 ? `+${v.toFixed(1)}` : v.toFixed(1), "Evaluación"]}
                />
                <Area type="monotone" dataKey="eval" stroke="rgb(var(--fg))" fill="url(#evalFill)" strokeWidth={1.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <aside className="space-y-4">
        {!revealed ? (
          <div className="card space-y-3">
            <h2 className="font-bold">1 · Primero tú</h2>
            <p className="text-sm text-muted">
              Antes de ver el motor, repasa la partida y anota dónde dudaste, qué plan tenías y qué jugada te
              preocupa. Así se entrena el criterio propio.
            </p>
            <textarea
              className="input min-h-32"
              placeholder="Ej.: En la jugada 14 no sabía si cambiar damas. Creo que 22…Tc8 fue un error."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            <button className="btn-primary w-full" onClick={saveNotes}>
              Guardar y ver el análisis
            </button>
          </div>
        ) : (
          <div className="card space-y-3">
            <h2 className="font-bold">2 · Lo que dice el motor</h2>
            {(game.analysis_status === "pending" || game.analysis_status === "running") && (
              <p className="animate-pulse text-sm text-muted">Stockfish está analizando la partida… suele tardar uno o dos minutos.</p>
            )}
            {game.analysis_status === "error" && (
              <div className="text-sm text-bad">
                El análisis falló.{" "}
                <button className="underline" onClick={() => api(`/games/${game.id}/reanalyze`, { method: "POST" }).then(load)}>
                  Reintentar
                </button>
              </div>
            )}
            {ready && (
              <>
                <div className="grid grid-cols-4 gap-2 text-center text-sm">
                  <div className="rounded-xl bg-panel2 p-2">
                    <div className="text-lg font-bold">{game.accuracy ?? "—"}%</div>
                    <div className="text-xs text-muted">Precisión</div>
                  </div>
                  <div className="rounded-xl bg-panel2 p-2">
                    <div className="text-lg font-bold text-tactics">{summary.inaccuracy}</div>
                    <div className="text-xs text-muted">Imprecis.</div>
                  </div>
                  <div className="rounded-xl bg-panel2 p-2">
                    <div className="text-lg font-bold text-rush">{summary.mistake}</div>
                    <div className="text-xs text-muted">Errores</div>
                  </div>
                  <div className="rounded-xl bg-panel2 p-2">
                    <div className="text-lg font-bold text-bad">{summary.blunder}</div>
                    <div className="text-xs text-muted">Graves</div>
                  </div>
                </div>
                {current ? (
                  <div className="rounded-xl bg-panel2 p-3 text-sm">
                    <div className="flex justify-between">
                      <span className={`font-bold ${CLASS_TEXT[current.classification]}`}>
                        {Math.ceil(current.ply / 2)}
                        {current.ply % 2 ? "." : "…"} {current.san}
                        {CLASS_SYMBOL[current.classification]} · {CLASS_LABEL[current.classification]}
                      </span>
                      <span className="font-mono">{evalText(current)}</span>
                    </div>
                    {current.best_san && current.best_uci !== current.uci && (
                      <p className="mt-1">
                        Mejor era <b className="text-good">{current.best_san}</b>
                        {current.pv_san && <span className="text-muted"> · {current.pv_san}</span>}
                      </p>
                    )}
                    <p className="mt-1 text-xs text-muted">
                      {PHASE_LABEL[current.phase]}
                      {current.error_type ? ` · ${current.error_type}` : ""}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-muted">Usa ← → o pulsa una jugada. La flecha verde marca la mejor alternativa.</p>
                )}
              </>
            )}
            {opening?.deviation && opening.deviation.type !== "end" && (
              <button
                className="w-full rounded-xl border border-openings/40 bg-openings/10 p-3 text-left text-sm"
                onClick={() => setPly(Math.max(0, opening.deviation!.ply - 1))}
              >
                <div className="text-xs font-semibold text-openings">Repertorio</div>
                {opening.deviation.type === "you"
                  ? `En la jugada ${Math.ceil(opening.deviation.ply / 2)} te saliste: jugaste ${opening.deviation.san} y tu repertorio dice ${opening.deviation.expected?.join(" / ")}.`
                  : `Tu rival se salió del repertorio con ${opening.deviation.san}. Prepárale una respuesta en Aperturas.`}
              </button>
            )}
            {game.user_notes && game.user_notes !== "—" && (
              <div className="rounded-xl border border-line p-3 text-sm">
                <div className="mb-1 text-xs font-semibold text-muted">Tus dudas</div>
                <p className="whitespace-pre-wrap">{game.user_notes}</p>
              </div>
            )}
            {!game.reviewed ? (
              <button className="btn-primary w-full" onClick={markReviewed}>
                Marcar como revisada
              </button>
            ) : (
              <p className="text-center text-sm text-good">✓ Partida revisada</p>
            )}
          </div>
        )}

        <MoveTable positions={positions} analysis={showEngine ? analysis : []} ply={ply} onPick={setPly} />
        <Link to="/partidas" className="block text-center text-sm text-muted underline">
          Todas las partidas
        </Link>
      </aside>
    </div>
  );
}

function MoveTable({
  positions,
  analysis,
  ply,
  onPick,
}: {
  positions: Position[];
  analysis: MoveAnalysis[];
  ply: number;
  onPick: (ply: number) => void;
}) {
  const rows = [];
  for (let i = 1; i < positions.length; i += 2) rows.push([i, i + 1]);
  const cell = (p: number) => {
    if (p >= positions.length) return <span />;
    const a = analysis[p - 1];
    return (
      <button
        onClick={() => onPick(p)}
        className={`rounded px-1.5 py-0.5 text-left font-medium ${ply === p ? "bg-play/25" : "hover:bg-panel2"} ${
          a ? CLASS_TEXT[a.classification] : ""
        }`}
      >
        {positions[p].san}
        {a ? CLASS_SYMBOL[a.classification] : ""}
      </button>
    );
  };
  return (
    <div className="card max-h-80 overflow-y-auto p-2 text-sm">
      <div className="grid grid-cols-[2.5rem_1fr_1fr] gap-x-1">
        {rows.map(([w, b], i) => (
          <div key={w} className="contents">
            <span className="py-0.5 text-right text-muted">{i + 1}.</span>
            {cell(w)}
            {cell(b)}
          </div>
        ))}
      </div>
    </div>
  );
}
