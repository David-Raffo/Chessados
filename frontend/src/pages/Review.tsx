import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Chess } from "chess.js";
import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Board, { toDests, turnColor, uciToKeys, type Color, type DrawShape, type Key } from "../components/Board";
import { api } from "../lib/api";
import { Engine } from "../lib/engine";
import { sound } from "../lib/sound";
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

const winChance = (cp: number) => 1 / (1 + Math.exp(-0.00368208 * cp));

const ANALYSING = ["pending", "running", "quick", "refining"];

function cpText(cp: number): string {
  if (Math.abs(cp) >= 9000) return `#${cp > 0 ? "" : "-"}${10000 - Math.abs(cp)}`;
  return `${cp > 0 ? "+" : ""}${(cp / 100).toFixed(1)}`;
}

/** Posición tras aplicar una lista de jugadas UCI a un FEN. */
function playFrom(fen: string, moves: string[]): Chess {
  const c = new Chess(fen);
  for (const m of moves) c.move({ from: m.slice(0, 2), to: m.slice(2, 4), promotion: m[4] ?? "q" });
  return c;
}

/** SAN de una línea UCI desde un FEN (se para en la primera jugada ilegal). */
function sanLine(fen: string, moves: string[]): string[] {
  const c = new Chess(fen);
  const out: string[] = [];
  for (const m of moves) {
    try {
      out.push(c.move({ from: m.slice(0, 2), to: m.slice(2, 4), promotion: m[4] }).san);
    } catch {
      break;
    }
  }
  return out;
}

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
  // Variante explorada a mano desde la jugada `varBase` de la partida (vacía = línea de la partida)
  const [varBase, setVarBase] = useState(0);
  const [variation, setVariation] = useState<string[]>([]);
  const [live, setLive] = useState<{ fen: string; cp: number; pv: string[] } | null>(null);
  const engine = useRef<Engine | null>(null);
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

  // Mientras el worker analiza (primero rápido, luego en profundidad) se consulta cada 2 s
  useEffect(() => {
    if (!game || !ANALYSING.includes(game.analysis_status)) return;
    const t = window.setTimeout(load, 2000);
    return () => window.clearTimeout(t);
  }, [game, load]);

  const positions = useMemo(() => (game ? parsePositions(game.pgn) : []), [game?.pgn]); // eslint-disable-line react-hooks/exhaustive-deps
  const analysis = game?.analysis ?? [];
  const ready = !!game && ["quick", "refining", "done"].includes(game.analysis_status) && analysis.length > 0;
  const showEngine = revealed && ready;
  const current = ply > 0 ? analysis[ply - 1] : undefined;
  const inVariation = variation.length > 0;

  // Posición que se ve en el tablero: la de la partida o la de la variante
  const board = useMemo(() => {
    const base = positions[Math.min(inVariation ? varBase : ply, positions.length - 1)];
    if (!base) return null;
    const c = inVariation ? playFrom(base.fen, variation) : new Chess(base.fen);
    const last = inVariation ? uciToKeys(variation[variation.length - 1]) : base.lastMove;
    return { chess: c, fen: c.fen(), lastMove: last as Key[] | undefined };
  }, [positions, ply, varBase, variation, inVariation]);

  const goTo = useCallback(
    (p: number) => {
      setVariation([]);
      setPly(Math.max(0, Math.min(positions.length - 1, p)));
    },
    [positions.length],
  );

  // Stockfish en el navegador para las variantes: arranca al ver el análisis
  useEffect(() => {
    if (!revealed) return;
    const eng = new Engine();
    eng.setOptions([["UCI_LimitStrength", "false"], ["Skill Level", 20], ["Hash", 32]]).catch(() => undefined);
    engine.current = eng;
    return () => {
      eng.terminate();
      engine.current = null;
    };
  }, [revealed]);

  // Evaluación en vivo de la posición de la variante (se ignoran resultados de posiciones ya dejadas atrás)
  const latestFen = useRef("");
  useEffect(() => {
    if (!inVariation || !board || !engine.current) return;
    const fen = board.fen;
    latestFen.current = fen;
    if (board.chess.isGameOver()) {
      const cp = board.chess.isCheckmate() ? (board.chess.turn() === "w" ? -10000 : 10000) : 0;
      setLive({ fen, cp, pv: [] });
      return;
    }
    engine.current
      .evaluate(fen, 16)
      .then((r) => {
        if (latestFen.current === fen) setLive({ fen, ...r });
      })
      .catch(() => undefined); // motor cerrado al salir de la revisión
  }, [board, inVariation]);

  function onBoardMove(from: Key, to: Key) {
    if (!board) return;
    const c = new Chess(board.fen);
    let m;
    try {
      m = c.move({ from, to, promotion: "q" });
    } catch {
      return;
    }
    if (m.captured) sound.capture();
    else sound.move();
    const uci = `${from}${to}${m.promotion ?? ""}`;
    // Si coincide con la jugada de la partida, se sigue la partida
    const next = positions[ply + 1];
    if (!inVariation && next?.lastMove && `${next.lastMove[0]}${next.lastMove[1]}` === uci.slice(0, 4) && !m.promotion) {
      setPly(ply + 1);
      return;
    }
    if (!inVariation) setVarBase(ply);
    setVariation((v) => [...v, uci]);
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === "TEXTAREA") return;
      if (inVariation) {
        if (e.key === "ArrowLeft") setVariation((v) => v.slice(0, -1));
        if (e.key === "Escape") setVariation([]);
        return;
      }
      if (e.key === "ArrowLeft") setPly((p) => Math.max(0, p - 1));
      if (e.key === "ArrowRight") setPly((p) => Math.min(positions.length - 1, p + 1));
      if (e.key === "ArrowUp") setPly(0);
      if (e.key === "ArrowDown") setPly(positions.length - 1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [positions.length, inVariation]);

  const liveNow = inVariation && live && board && live.fen === board.fen ? live : null;

  const shapes = useMemo((): DrawShape[] => {
    if (inVariation) {
      if (!liveNow?.pv[0]) return [];
      const [orig, dest] = uciToKeys(liveNow.pv[0]);
      return [{ orig, dest, brush: "blue" }];
    }
    // Como en chess.com: de la jugada que acaba de hacerse, en blanco la jugada y en verde la que había
    // que hacer en su lugar (lo mismo que cuenta el recuadro). Si fue la mejor, solo la verde.
    if (!showEngine || !current?.best_uci) return [];
    const [orig, dest] = uciToKeys(current.best_uci);
    const out: DrawShape[] = [];
    if (current.uci.slice(0, 4) !== current.best_uci.slice(0, 4)) {
      const [o, d] = uciToKeys(current.uci);
      out.push({ orig: o, dest: d, brush: "white" });
    }
    out.push({ orig, dest, brush: "green" });
    return out;
  }, [current, showEngine, inVariation, liveNow]);

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
    navigate("/jugar"); // revisada: a por la siguiente partida
  }

  if (error) return <p className="text-bad">{error}</p>;
  if (!game) return <p className="text-muted">Cargando partida…</p>;

  const whiteName = game.user_color === "white" ? "Tú" : opponentName(game);
  const blackName = game.user_color === "black" ? "Tú" : opponentName(game);
  const evalCp = liveNow ? liveNow.cp : showEngine ? (current ? current.eval_cp : analysis[0] ? 20 : 0) : 0;
  const varSan = inVariation ? sanLine(positions[varBase].fen, variation) : [];
  const liveLine = liveNow ? sanLine(liveNow.fen, liveNow.pv.slice(0, 8)) : [];
  const startMove = Math.floor(varBase / 2) + 1;

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
            {board && (
              <Board
                fen={board.fen}
                orientation={orientation}
                lastMove={board.lastMove}
                shapes={shapes}
                movable={revealed ? turnColor(board.chess) : undefined}
                dests={toDests(board.chess)}
                check={board.chess.inCheck()}
                onMove={onBoardMove}
              />
            )}
          </div>
        </div>

        <div className="flex justify-center gap-2">
          {[
            ["⏮", () => goTo(0)],
            ["◀", () => (inVariation ? setVariation((v) => v.slice(0, -1)) : goTo(ply - 1))],
            ["▶", () => !inVariation && goTo(ply + 1)],
            ["⏭", () => goTo(positions.length - 1)],
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
                onClick={(e) => e?.activeLabel != null && goTo(Number(e.activeLabel))}
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
              <p className="animate-pulse text-sm text-muted">Stockfish está analizando la partida… un momento.</p>
            )}
            {(game.analysis_status === "quick" || game.analysis_status === "refining") && (
              <p className="text-xs text-muted">
                <span className="animate-pulse">●</span> Análisis rápido listo; Stockfish lo está afinando en profundidad.
              </p>
            )}
            {inVariation && (
              <div className="space-y-2 rounded-xl border border-play/40 bg-play/10 p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-play">Explorando una variante</span>
                  <span className="font-mono font-bold">{liveNow ? cpText(liveNow.cp) : "…"}</span>
                </div>
                <p className="font-medium">
                  {varSan.map((san, i) => {
                    const plyNo = varBase + i + 1;
                    const num = plyNo % 2 ? `${Math.ceil(plyNo / 2)}. ` : i === 0 ? `${startMove}… ` : "";
                    return (
                      <span key={i}>
                        {num}
                        {san}{" "}
                      </span>
                    );
                  })}
                </p>
                {liveLine.length > 0 && (
                  <p className="text-muted">
                    Mejor: <b className="text-fg">{liveLine[0]}</b> · {liveLine.slice(1).join(" ")}
                  </p>
                )}
                {!liveNow && <p className="animate-pulse text-xs text-muted">Stockfish pensando…</p>}
                <div className="flex gap-2">
                  <button className="btn-ghost flex-1 py-1.5" onClick={() => setVariation((v) => v.slice(0, -1))}>
                    ◀ Deshacer
                  </button>
                  <button className="btn-primary flex-1 py-1.5" onClick={() => setVariation([])}>
                    Volver a la partida
                  </button>
                </div>
              </div>
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
                {inVariation ? null : current ? (
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
                        <button
                          className="ml-1 text-play underline"
                          onClick={() => {
                            // Vuelve a la posición de antes de tu jugada y juega la buena como variante
                            setVarBase(current.ply - 1);
                            setVariation([current.best_uci!]);
                          }}
                        >
                          Verla en el tablero
                        </button>
                      </p>
                    )}
                    <p className="mt-1 text-xs text-muted">
                      {PHASE_LABEL[current.phase]}
                      {current.error_type ? ` · ${current.error_type}` : ""}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-muted">
                    Usa ← → o pulsa una jugada. De cada jugada, la flecha blanca marca la que se hizo y la verde la que había que
                    hacer. Mueve las piezas para probar otros caminos: Stockfish los evalúa al momento.
                  </p>
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

        <MoveTable positions={positions} analysis={showEngine ? analysis : []} ply={inVariation ? -1 : ply} onPick={goTo} />
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
