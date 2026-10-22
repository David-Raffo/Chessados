import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Chess } from "chess.js";
import confetti from "canvas-confetti";
import Board, { isPromotion, toDests, turnColor, type Color, type Key } from "../components/Board";
import { Captured, material, type MaterialInfo } from "../components/Material";
import Promotion from "../components/Promotion";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Engine, strengthFor } from "../lib/engine";
import { formatClock } from "../lib/labels";
import { sound } from "../lib/sound";
import { useActivity } from "../lib/useActivity";

const TIME_CONTROLS = [
  { id: "15+10", minutes: 15, inc: 10, label: "15+10", hint: "Recomendado" },
  { id: "30+0", minutes: 30, inc: 0, label: "30+0", hint: "Partida lenta" },
  { id: "10+5", minutes: 10, inc: 5, label: "10+5", hint: "Rápida" },
  { id: "5+3", minutes: 5, inc: 3, label: "5+3", hint: "Blitz" },
];

const MAIA_LEVELS = [1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900];

interface Setup {
  rival: "stockfish" | "maia";
  maiaLevel: number;
  ladder: boolean;
  elo: number;
  color: Color | "random";
  tc: (typeof TIME_CONTROLS)[number];
}

interface Outcome {
  result: "1-0" | "0-1" | "1/2-1/2";
  reason: string;
}

interface SaveResult {
  game: { id: number };
  rating_before: number;
  rating_after: number;
  ladder_before: number;
  ladder_after: number;
}

export default function Play() {
  const { user, setUser } = useAuth();
  const [params] = useSearchParams();
  const [lock, setLock] = useState<{ locked: boolean; game_id: number | null; ladder_elo: number } | null>(null);
  const [maia, setMaia] = useState(false);
  const [setup, setSetup] = useState<Setup>({
    rival: "stockfish",
    maiaLevel: Math.max(1100, Math.min(1900, Math.round((user?.ladder_elo ?? 1200) / 100) * 100)),
    ladder: true,
    elo: user?.ladder_elo ?? 1200,
    color: "random",
    tc: TIME_CONTROLS.find((t) => t.id === params.get("tc")) ?? TIME_CONTROLS[0],
  });
  const [game, setGame] = useState<{ color: Color; elo: number; setup: Setup; key: number } | null>(null);

  useEffect(() => {
    api("/games/can-play").then(setLock).catch(() => setLock({ locked: false, game_id: null, ladder_elo: 1200 }));
  }, [game]);

  useEffect(() => {
    api<{ available: boolean }>("/maia/status").then((r) => setMaia(r.available)).catch(() => undefined);
  }, []);

  function start() {
    const color: Color = setup.color === "random" ? (Math.random() < 0.5 ? "white" : "black") : setup.color;
    const isMaia = setup.rival === "maia";
    const elo = isMaia ? setup.maiaLevel : setup.ladder ? lock?.ladder_elo ?? user?.ladder_elo ?? 1200 : setup.elo;
    setGame({ color, elo, setup: { ...setup, ladder: setup.ladder && !isMaia }, key: Date.now() });
  }

  if (game) {
    return (
      <GameView
        key={game.key}
        color={game.color}
        elo={game.elo}
        setup={game.setup}
        onExit={() => setGame(null)}
        onSaved={(r) => user && setUser({ ...user, ladder_elo: r.ladder_after })}
      />
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <header>
        <h1 className="text-2xl font-extrabold">Jugar contra la máquina</h1>
        <p className="text-muted">Stockfish con fuerza ajustable. Juega lento y revisa cada partida.</p>
      </header>

      {lock?.locked && (
        <div className="card border-tactics/50 bg-tactics/10">
          <p className="font-semibold">Revisa tu última partida antes de jugar otra.</p>
          <p className="mb-3 text-sm text-muted">
            Analizar tus propias partidas es lo que más rinde. Puedes desactivar este bloqueo en Ajustes.
          </p>
          <Link className="btn-primary" to={`/revision/${lock.game_id}`}>
            Revisar ahora
          </Link>
        </div>
      )}

      <section className="card space-y-5">
        <div>
          <label className="label">Motor</label>
          <div className="grid grid-cols-2 gap-2">
            <button
              className={`rounded-xl border p-3 text-left ${setup.rival === "stockfish" ? "border-play bg-play/10" : "border-line"}`}
              onClick={() => setSetup({ ...setup, rival: "stockfish" })}
            >
              <div className="font-semibold">Stockfish</div>
              <div className="text-xs text-muted">Fuerza ajustable de 400 a 3000</div>
            </button>
            <button
              disabled={!maia}
              className={`rounded-xl border p-3 text-left disabled:opacity-50 ${setup.rival === "maia" ? "border-play bg-play/10" : "border-line"}`}
              onClick={() => setSetup({ ...setup, rival: "maia" })}
            >
              <div className="font-semibold">Maia · juego humano</div>
              <div className="text-xs text-muted">{maia ? "Imita a jugadores de 1100 a 1900" : "No disponible"}</div>
            </button>
          </div>
        </div>

        {setup.rival === "maia" ? (
          <div>
            <label className="label">Nivel de Maia</label>
            <div className="flex flex-wrap gap-1.5">
              {MAIA_LEVELS.map((l) => (
                <button
                  key={l}
                  className={`chip ${setup.maiaLevel === l ? "chip-on" : ""}`}
                  onClick={() => setSetup({ ...setup, maiaLevel: l })}
                >
                  {l}
                </button>
              ))}
            </div>
            <p className="mt-2 text-xs text-muted">
              Maia comete los errores que cometería una persona de ese nivel. Más realista que un Stockfish debilitado.
            </p>
          </div>
        ) : (
        <div>
          <label className="label">Rival</label>
          <div className="grid grid-cols-2 gap-2">
            <button
              className={`rounded-xl border p-3 text-left ${setup.ladder ? "border-play bg-play/10" : "border-line"}`}
              onClick={() => setSetup({ ...setup, ladder: true })}
            >
              <div className="font-semibold">Escalera · {lock?.ladder_elo ?? user?.ladder_elo}</div>
              <div className="text-xs text-muted">Ganas: +50. Pierdes: −25.</div>
            </button>
            <button
              className={`rounded-xl border p-3 text-left ${!setup.ladder ? "border-play bg-play/10" : "border-line"}`}
              onClick={() => setSetup({ ...setup, ladder: false })}
            >
              <div className="font-semibold">ELO libre</div>
              <div className="text-xs text-muted">Elige la fuerza exacta</div>
            </button>
          </div>
          {!setup.ladder && (
            <div className="mt-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted">Fuerza de Stockfish</span>
                <span className="font-bold">{setup.elo}</span>
              </div>
              <input
                type="range"
                min={400}
                max={3000}
                step={50}
                value={setup.elo}
                onChange={(e) => setSetup({ ...setup, elo: Number(e.target.value) })}
                className="w-full accent-[rgb(var(--play))]"
              />
            </div>
          )}
        </div>
        )}

        <div>
          <label className="label">Color</label>
          <div className="flex gap-2">
            {(
              [
                ["white", "Blancas"],
                ["random", "Aleatorio"],
                ["black", "Negras"],
              ] as const
            ).map(([c, label]) => (
              <button
                key={c}
                className={`chip ${setup.color === c ? "chip-on" : ""}`}
                onClick={() => setSetup({ ...setup, color: c })}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="label">Ritmo</label>
          <div className="grid grid-cols-4 gap-2">
            {TIME_CONTROLS.map((t) => (
              <button
                key={t.id}
                className={`rounded-xl border p-2 text-center ${setup.tc.id === t.id ? "border-play bg-play/10" : "border-line"}`}
                onClick={() => setSetup({ ...setup, tc: t })}
              >
                <div className="font-bold">{t.label}</div>
                <div className="text-[11px] text-muted">{t.hint}</div>
              </button>
            ))}
          </div>
        </div>

        <button className="btn-primary w-full py-3 text-lg" disabled={!lock || lock.locked} onClick={start}>
          Empezar partida
        </button>
      </section>
    </div>
  );
}

function GameView({
  color,
  elo,
  setup,
  onExit,
  onSaved,
}: {
  color: Color;
  elo: number;
  setup: Setup;
  onExit: () => void;
  onSaved: (r: SaveResult) => void;
}) {
  const navigate = useNavigate();
  const chess = useRef(new Chess());
  const engine = useRef<Engine | null>(null);
  const [fen, setFen] = useState(chess.current.fen());
  const [lastMove, setLastMove] = useState<Key[] | undefined>();
  const [orientation, setOrientation] = useState<Color>(color);
  const [promo, setPromo] = useState<{ from: Key; to: Key } | null>(null);
  const [thinking, setThinking] = useState(false);
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [saved, setSaved] = useState<SaveResult | null>(null);
  const [saveError, setSaveError] = useState("");
  const [engineError, setEngineError] = useState("");
  const clocks = useRef({ white: setup.tc.minutes * 60_000, black: setup.tc.minutes * 60_000 });
  const [clockView, setClockView] = useState(clocks.current);
  const lastTick = useRef<number | null>(null);
  const over = useRef(false);
  const ping = useActivity(outcome ? null : "play", "game");
  const strength = useMemo(() => strengthFor(elo), [elo]);
  const isMaia = setup.rival === "maia";
  const rivalName = `${isMaia ? "Maia" : "Stockfish"} ${elo}`;

  const finish = useCallback((o: Outcome) => {
    if (over.current) return;
    over.current = true;
    setOutcome(o);
    sound.end();
  }, []);

  const checkEnd = useCallback(() => {
    const c = chess.current;
    if (c.isCheckmate()) {
      finish({ result: c.turn() === "w" ? "0-1" : "1-0", reason: "Jaque mate" });
    } else if (c.isStalemate()) finish({ result: "1/2-1/2", reason: "Rey ahogado" });
    else if (c.isThreefoldRepetition()) finish({ result: "1/2-1/2", reason: "Triple repetición" });
    else if (c.isInsufficientMaterial()) finish({ result: "1/2-1/2", reason: "Material insuficiente" });
    else if (c.isDraw()) finish({ result: "1/2-1/2", reason: "Regla de los 50 movimientos" });
    return over.current;
  }, [finish]);

  const afterMove = useCallback(
    (mover: Color, captured: boolean) => {
      // Incremento para quien acaba de mover
      clocks.current[mover] += setup.tc.inc * 1000;
      lastTick.current = performance.now();
      setClockView({ ...clocks.current });
      setFen(chess.current.fen());
      if (chess.current.inCheck()) sound.check();
      else if (captured) sound.capture();
      else sound.move();
      return checkEnd();
    },
    [checkEnd, setup.tc.inc],
  );

  const engineMove = useCallback(async () => {
    const eng = engine.current;
    if ((!eng && !isMaia) || over.current) return;
    setThinking(true);
    const engineColor: Color = color === "white" ? "black" : "white";
    const remaining = clocks.current[engineColor];
    const thinkMs = Math.round(Math.max(150, Math.min(3000, remaining / 40 + setup.tc.inc * 400)));
    const fenBefore = chess.current.fen();
    const started = performance.now();
    try {
      const uci = isMaia
        ? (await api<{ move: string }>("/maia/move", { body: { fen: fenBefore, level: elo } })).move
        : await eng!.bestMove(fenBefore, strength.go(thinkMs));
      // Pausa mínima para que la jugada no aparezca de golpe (Maia responde al instante: algo más humana)
      const minWait = isMaia ? Math.min(thinkMs, 600 + Math.random() * 900) : 350;
      const wait = minWait - (performance.now() - started);
      if (wait > 0) await new Promise((r) => setTimeout(r, wait));
      if (over.current || chess.current.fen() !== fenBefore || !uci || uci === "(none)") return;
      const move = chess.current.move({ from: uci.slice(0, 2), to: uci.slice(2, 4), promotion: uci[4] ?? "q" });
      setLastMove([move.from as Key, move.to as Key]);
      afterMove(engineColor, !!move.captured);
      ping();
    } catch (e) {
      setEngineError(`El motor ha fallado: ${(e as Error).message}`);
    } finally {
      setThinking(false);
    }
  }, [afterMove, color, elo, isMaia, ping, setup.tc.inc, strength]);

  // Arranque del motor
  useEffect(() => {
    if (isMaia) {
      lastTick.current = performance.now();
      if (color === "black") engineMove();
      return;
    }
    const eng = new Engine();
    engine.current = eng;
    eng
      .setOptions([...strength.options, ["Hash", 16]])
      .then(() => eng.newGame())
      .then(() => {
        lastTick.current = performance.now();
        if (color === "black") engineMove();
      })
      .catch((e) => setEngineError(String(e)));
    return () => {
      eng.terminate();
      engine.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reloj
  useEffect(() => {
    const id = window.setInterval(() => {
      if (over.current || lastTick.current == null) return;
      const now = performance.now();
      const side = turnColor(chess.current);
      clocks.current[side] -= now - lastTick.current;
      lastTick.current = now;
      if (clocks.current[side] <= 0) {
        clocks.current[side] = 0;
        finish({ result: side === "white" ? "0-1" : "1-0", reason: "Tiempo agotado" });
      }
      setClockView({ ...clocks.current });
    }, 100);
    return () => window.clearInterval(id);
  }, [finish]);

  // Guardar la partida al terminar
  useEffect(() => {
    if (!outcome) return;
    const c = chess.current;
    const date = new Date();
    c.setHeader("Event", `Chessados · ${setup.tc.label}`);
    c.setHeader("Site", "Chessados");
    c.setHeader("Date", `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`);
    c.setHeader("White", color === "white" ? "Tú" : rivalName);
    c.setHeader("Black", color === "black" ? "Tú" : rivalName);
    c.setHeader("Result", outcome.result);
    c.setHeader("TimeControl", `${setup.tc.minutes * 60}+${setup.tc.inc}`);
    c.setHeader("Termination", outcome.reason);
    api<SaveResult>("/games", {
      body: {
        pgn: c.pgn(),
        user_color: color,
        result: outcome.result,
        opponent: setup.rival,
        opponent_elo: elo,
        time_control: setup.tc.id,
        ladder: setup.ladder,
      },
    })
      .then((r) => {
        setSaved(r);
        onSaved(r);
        const won = (outcome.result === "1-0") === (color === "white") && outcome.result !== "1/2-1/2";
        if (won) confetti({ particleCount: 90, spread: 70, origin: { y: 0.6 }, disableForReducedMotion: true });
      })
      .catch((e) => setSaveError(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [outcome]);

  function play(from: Key, to: Key, promotion?: string) {
    if (over.current) return;
    if (!promotion && isPromotion(chess.current, from, to)) {
      setPromo({ from, to });
      return;
    }
    try {
      const move = chess.current.move({ from, to, promotion });
      setLastMove([from, to]);
      if (!afterMove(color, !!move.captured)) engineMove();
    } catch {
      setFen(chess.current.fen()); // jugada ilegal: devuelve la pieza
    }
  }

  const userTurn = !outcome && turnColor(chess.current) === color && !thinking;
  const dests = useMemo(() => toDests(chess.current), [fen]);
  const mat = useMemo(() => material(fen), [fen]);
  const history = chess.current.history();
  const opp: Color = color === "white" ? "black" : "white";
  const top = orientation === color ? opp : color;
  const bottom = top === color ? opp : color;

  const won = outcome && outcome.result !== "1/2-1/2" && (outcome.result === "1-0") === (color === "white");
  const title = !outcome ? "" : outcome.result === "1/2-1/2" ? "Tablas" : won ? "¡Has ganado!" : "Has perdido";

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
      <div className="mx-auto w-full max-w-[min(100%,calc(100vh-10rem))]">
        <ClockRow
          name={top === color ? "Tú" : rivalName}
          side={top}
          info={mat}
          ms={clockView[top]}
          active={!outcome && turnColor(chess.current) === top}
          thinking={thinking && top !== color}
        />
        <div className="relative my-2">
          <Board
            fen={fen}
            orientation={orientation}
            movable={userTurn ? color : undefined}
            dests={dests}
            lastMove={lastMove}
            check={chess.current.inCheck()}
            onMove={(f, t) => play(f, t)}
          />
          {promo && (
            <Promotion
              color={color}
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
        <ClockRow
          name={bottom === color ? "Tú" : rivalName}
          side={bottom}
          info={mat}
          ms={clockView[bottom]}
          active={!outcome && turnColor(chess.current) === bottom}
          thinking={thinking && bottom !== color}
        />
      </div>

      <aside className="space-y-4">
        {outcome ? (
          <div className="card animate-pop space-y-3">
            <div>
              <h2 className={`text-2xl font-extrabold ${won ? "text-good" : outcome.result === "1/2-1/2" ? "" : "text-bad"}`}>
                {title}
              </h2>
              <p className="text-muted">{outcome.reason}</p>
            </div>
            {saved && (
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="rounded-xl bg-panel2 p-2">
                  <div className="text-muted">ELO partidas</div>
                  <div className="font-bold">
                    {saved.rating_after}{" "}
                    <Delta value={saved.rating_after - saved.rating_before} />
                  </div>
                </div>
                {setup.ladder && (
                  <div className="rounded-xl bg-panel2 p-2">
                    <div className="text-muted">Escalera</div>
                    <div className="font-bold">
                      {saved.ladder_after} <Delta value={saved.ladder_after - saved.ladder_before} />
                    </div>
                  </div>
                )}
              </div>
            )}
            {saveError && <p className="text-sm text-bad">No se pudo guardar: {saveError}</p>}
            <button
              className="btn-primary w-full"
              disabled={!saved}
              onClick={() => saved && navigate(`/revision/${saved.game.id}`)}
            >
              Revisar la partida
            </button>
            <button className="btn-ghost w-full" onClick={onExit}>
              Volver
            </button>
          </div>
        ) : (
          <div className="card space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold">{rivalName}</span>
              <span className="text-sm text-muted">{setup.tc.label}{setup.ladder ? " · Escalera" : ""}</span>
            </div>
            <div className="flex gap-2">
              <button className="btn-ghost flex-1" onClick={() => setOrientation(orientation === "white" ? "black" : "white")}>
                Girar
              </button>
              <button
                className="btn-ghost flex-1 text-bad"
                onClick={() => finish({ result: color === "white" ? "0-1" : "1-0", reason: "Abandono" })}
              >
                Abandonar
              </button>
            </div>
          </div>
        )}
        {engineError && <p className="text-sm text-bad">{engineError}</p>}
        <MoveList history={history} />
      </aside>
    </div>
  );
}

function Delta({ value }: { value: number }) {
  if (!value) return <span className="text-muted">±0</span>;
  return <span className={value > 0 ? "text-good" : "text-bad"}>{value > 0 ? `+${value}` : value}</span>;
}

function ClockRow({
  name,
  side,
  info,
  ms,
  active,
  thinking,
}: {
  name: string;
  side: Color;
  info: MaterialInfo;
  ms: number;
  active: boolean;
  thinking: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1">
        <span className="font-semibold">
          {name}
          {thinking && <span className="ml-2 animate-pulse text-sm text-muted">pensando…</span>}
        </span>
        <Captured info={info} side={side} />
      </span>
      <span
        className={`rounded-lg px-3 py-1 font-mono text-xl font-bold tabular-nums ${
          active ? (ms < 30_000 ? "bg-bad text-white" : "bg-fg text-bg") : "bg-panel2 text-muted"
        }`}
      >
        {formatClock(ms)}
      </span>
    </div>
  );
}

function MoveList({ history }: { history: string[] }) {
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => {
    end.current?.scrollIntoView({ block: "nearest" });
  }, [history.length]);
  const rows = [];
  for (let i = 0; i < history.length; i += 2) rows.push([history[i], history[i + 1]]);
  return (
    <div className="card max-h-72 overflow-y-auto p-2 text-sm">
      {rows.length === 0 && <p className="p-2 text-muted">Sin jugadas todavía.</p>}
      <div className="grid grid-cols-[2.5rem_1fr_1fr] gap-x-2">
        {rows.map(([w, b], i) => (
          <div key={i} className="contents">
            <span className="py-0.5 text-right text-muted">{i + 1}.</span>
            <span className="py-0.5 font-medium">{w}</span>
            <span className="py-0.5 font-medium">{b ?? ""}</span>
          </div>
        ))}
      </div>
      <div ref={end} />
    </div>
  );
}
