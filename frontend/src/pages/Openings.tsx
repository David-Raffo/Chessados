import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Chess } from "chess.js";
import Board, { toDests, turnColor, uciToKeys, type Color, type DrawShape, type Key } from "../components/Board";
import { api } from "../lib/api";
import { sound } from "../lib/sound";
import { useActivity } from "../lib/useActivity";

interface Line {
  id: number;
  fen: string;
  move: string;
  san: string;
  comment: string | null;
}

interface TrainItem {
  line_id: number;
  color: Color;
  path: string[];
  move: string;
  san: string;
  comment: string | null;
}

interface Deviation {
  game_id: number;
  user_color: Color;
  opponent: string;
  opponent_elo: number | null;
  played_at: string;
  opening: { eco: string; name: string } | null;
  deviation: {
    ply: number;
    type: "you" | "opponent" | "end";
    san: string | null;
    expected: string[] | null;
    path?: string[];
  } | null;
}

/** Clave de posición igual que en el servidor: sin contadores de jugadas. */
const key = (fen: string) => fen.split(" ").slice(0, 4).join(" ");

function playPath(path: string[]): Chess {
  const c = new Chess();
  for (const uci of path) c.move({ from: uci.slice(0, 2), to: uci.slice(2, 4), promotion: uci[4] });
  return c;
}

export default function Openings() {
  const [params, setParams] = useSearchParams();
  const tab = (params.get("tab") as "train" | "edit" | "deviations") ?? "train";
  const [editStart, setEditStart] = useState<{ color: Color; path: string[] } | null>(null);
  useActivity("openings", tab === "train" ? "repertoire-train" : "repertoire");

  const setTab = (t: string) => setParams({ tab: t });

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-extrabold">Aperturas</h1>
        <p className="text-muted">Tu repertorio propio, entrenado con repetición espaciada.</p>
      </header>
      <div className="flex flex-wrap gap-2">
        {(
          [
            ["train", "Entrenar"],
            ["edit", "Mi repertorio"],
            ["deviations", "Desviaciones en mis partidas"],
          ] as const
        ).map(([t, label]) => (
          <button key={t} className={`chip ${tab === t ? "chip-on" : ""}`} onClick={() => setTab(t)}>
            {label}
          </button>
        ))}
      </div>
      {tab === "train" && <Train onEdit={() => setTab("edit")} />}
      {tab === "edit" && <Editor start={editStart} />}
      {tab === "deviations" && (
        <Deviations
          onOpen={(color, path) => {
            setEditStart({ color, path });
            setTab("edit");
          }}
        />
      )}
    </div>
  );
}

// --- Editor del repertorio ---------------------------------------------------

function Editor({ start }: { start: { color: Color; path: string[] } | null }) {
  const [color, setColor] = useState<Color>(start?.color ?? "white");
  const [path, setPath] = useState<string[]>(start?.path ?? []);
  const [lines, setLines] = useState<Line[] | null>(null);
  const [name, setName] = useState<{ eco: string | null; name: string | null }>({ eco: null, name: null });
  const [msg, setMsg] = useState("");
  const [comment, setComment] = useState("");

  const load = useCallback(() => {
    api<{ lines: Line[] }>(`/openings/repertoire?color=${color}`).then((r) => setLines(r.lines));
  }, [color]);
  useEffect(load, [load]);

  const chess = useMemo(() => playPath(path), [path]);
  const here = useMemo(() => (lines ?? []).filter((l) => l.fen === key(chess.fen())), [lines, chess]);
  const userTurn = turnColor(chess) === color;
  const mine = userTurn ? here[0] : undefined;

  useEffect(() => {
    api<{ eco: string | null; name: string | null }>("/openings/name", { body: { moves: path } }).then(setName);
    setMsg("");
  }, [path]);
  useEffect(() => setComment(mine?.comment ?? ""), [mine]);

  const history = useMemo(() => {
    const c = new Chess();
    return path.map((uci) => c.move({ from: uci.slice(0, 2), to: uci.slice(2, 4), promotion: uci[4] }).san);
  }, [path]);

  const shapes: DrawShape[] = here.map((l) => {
    const [orig, dest] = uciToKeys(l.move);
    return { orig, dest, brush: userTurn ? "green" : "blue" };
  });

  async function onMove(from: Key, to: Key) {
    const c = new Chess(chess.fen());
    let m;
    try {
      m = c.move({ from, to, promotion: "q" });
    } catch {
      return;
    }
    const uci = `${from}${to}${m.promotion ?? ""}`;
    if (!here.some((l) => l.move === uci)) {
      const r = await api<Line & { replaced?: number }>("/openings/repertoire", {
        body: { color, fen: chess.fen(), move: uci },
      });
      setMsg(r.replaced ? `Sustituida tu jugada anterior (${r.replaced} posiciones borradas).` : `Añadida ${r.san}.`);
      load();
    }
    sound.move();
    setPath([...path, uci]);
  }

  async function remove(l: Line) {
    if (!window.confirm(`¿Borrar ${l.san} y todas las jugadas que cuelgan de ella?`)) return;
    await api(`/openings/repertoire/${l.id}`, { method: "DELETE" });
    load();
  }

  async function starter() {
    const r = await api<{ added: number }>(`/openings/starter/${color}`, { method: "POST" });
    setMsg(`Cargadas ${r.added} jugadas de ejemplo.`);
    load();
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="mx-auto w-full max-w-[min(100%,calc(100vh-14rem))]">
        <Board
          fen={chess.fen()}
          orientation={color}
          movable={turnColor(chess)}
          dests={toDests(chess)}
          lastMove={path.length ? uciToKeys(path[path.length - 1]) : undefined}
          shapes={shapes}
          onMove={onMove}
        />
      </div>
      <aside className="space-y-4">
        <div className="card space-y-3">
          <div className="flex gap-2">
            {(["white", "black"] as Color[]).map((c) => (
              <button
                key={c}
                className={`chip ${color === c ? "chip-on" : ""}`}
                onClick={() => {
                  setColor(c);
                  setPath([]);
                }}
              >
                Con {c === "white" ? "blancas" : "negras"}
              </button>
            ))}
          </div>
          <div>
            <div className="text-xs text-muted">{name.eco ?? "—"}</div>
            <div className="font-semibold">{name.name ?? "Posición inicial"}</div>
          </div>
          <div className="flex flex-wrap gap-1 text-sm">
            <button className="rounded px-1.5 hover:bg-panel2" onClick={() => setPath([])}>
              Inicio
            </button>
            {history.map((san, i) => (
              <button key={i} className="rounded px-1.5 hover:bg-panel2" onClick={() => setPath(path.slice(0, i + 1))}>
                {i % 2 === 0 ? `${i / 2 + 1}.` : ""}
                {san}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <button className="btn-ghost flex-1" disabled={!path.length} onClick={() => setPath(path.slice(0, -1))}>
              ← Atrás
            </button>
            <button className="btn-ghost flex-1" disabled={!path.length} onClick={() => setPath([])}>
              Al inicio
            </button>
          </div>
        </div>

        <div className="card space-y-2">
          <div className="text-sm font-semibold">
            {userTurn ? "Tu jugada en esta posición" : "Respuestas del rival que has preparado"}
          </div>
          {here.length === 0 && (
            <p className="text-sm text-muted">
              {userTurn ? "Haz tu jugada en el tablero para añadirla." : "Juega en el tablero las respuestas del rival que quieras preparar."}
            </p>
          )}
          {here.map((l) => (
            <div key={l.id} className="flex items-center gap-2">
              <button className="flex-1 rounded-lg bg-panel2 px-3 py-1.5 text-left font-semibold hover:bg-line" onClick={() => setPath([...path, l.move])}>
                {l.san}
              </button>
              <button className="text-sm text-bad hover:underline" onClick={() => remove(l)}>
                Borrar
              </button>
            </div>
          ))}
          {mine && (
            <div className="space-y-1 pt-2">
              <label className="label">Nota (te la recordará al entrenar)</label>
              <textarea className="input min-h-16 text-sm" value={comment} onChange={(e) => setComment(e.target.value)} />
              <button
                className="btn-ghost w-full"
                onClick={() =>
                  api("/openings/repertoire", { body: { color, fen: chess.fen(), move: mine.move, comment } }).then(() => {
                    setMsg("Nota guardada.");
                    load();
                  })
                }
              >
                Guardar nota
              </button>
            </div>
          )}
          {msg && <p className="text-sm text-muted">{msg}</p>}
        </div>

        {lines && lines.length === 0 && (
          <div className="card space-y-2 text-sm">
            <p>¿Empiezas de cero? Carga un repertorio sencillo y modifícalo a tu gusto.</p>
            <button className="btn-primary w-full" onClick={starter}>
              Cargar repertorio de ejemplo con {color === "white" ? "blancas" : "negras"}
            </button>
          </div>
        )}
        <p className="text-xs text-muted">{lines?.length ?? 0} jugadas en tu repertorio con {color === "white" ? "blancas" : "negras"}.</p>
      </aside>
    </div>
  );
}

// --- Entrenamiento -----------------------------------------------------------

function Train({ onEdit }: { onEdit: () => void }) {
  const [item, setItem] = useState<TrainItem | null>(null);
  const [empty, setEmpty] = useState(false);
  const [fen, setFen] = useState(new Chess().fen());
  const [lastMove, setLastMove] = useState<Key[] | undefined>();
  const [phase, setPhase] = useState<"replay" | "answer" | "good" | "bad">("replay");
  const [shapes, setShapes] = useState<DrawShape[]>([]);
  const [count, setCount] = useState({ good: 0, bad: 0 });
  const chess = useRef(new Chess());

  const next = useCallback(() => {
    setShapes([]);
    api<TrainItem | null>("/openings/train")
      .then((it) => {
        setEmpty(!it);
        setItem(it);
      })
      .catch(() => {
        setItem(null);
        setEmpty(true);
      });
  }, []);
  useEffect(next, [next]);

  // Reproduce la línea hasta la posición que toca recordar
  useEffect(() => {
    if (!item) return;
    chess.current = new Chess();
    setFen(chess.current.fen());
    setLastMove(undefined);
    setPhase("replay");
    let i = 0;
    const id = window.setInterval(() => {
      if (i >= item.path.length) {
        window.clearInterval(id);
        setPhase("answer");
        return;
      }
      const uci = item.path[i++];
      chess.current.move({ from: uci.slice(0, 2), to: uci.slice(2, 4), promotion: uci[4] });
      setFen(chess.current.fen());
      setLastMove(uciToKeys(uci));
    }, 220);
    return () => window.clearInterval(id);
  }, [item]);

  function onMove(from: Key, to: Key) {
    if (!item || phase !== "answer") return;
    const correct = `${from}${to}` === item.move.slice(0, 4);
    api(`/openings/train/${item.line_id}`, { body: { correct } });
    if (correct) {
      chess.current.move({ from, to, promotion: item.move[4] ?? "q" });
      setFen(chess.current.fen());
      setLastMove([from, to]);
      setPhase("good");
      setCount((c) => ({ ...c, good: c.good + 1 }));
      sound.good();
      window.setTimeout(next, 900);
    } else {
      setFen(chess.current.fen());
      const [orig, dest] = uciToKeys(item.move);
      setShapes([{ orig, dest, brush: "green" }]);
      setPhase("bad");
      setCount((c) => ({ ...c, bad: c.bad + 1 }));
      sound.bad();
    }
  }

  if (empty) {
    return (
      <div className="card space-y-3 text-center">
        <p className="text-lg font-semibold">No tienes jugadas pendientes de repaso hoy. 🎉</p>
        <p className="text-sm text-muted">Las jugadas vuelven cuando toca según la repetición espaciada. Mientras, amplía tu repertorio.</p>
        <button className="btn-ghost" onClick={onEdit}>
          Editar repertorio
        </button>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
      <div className={`mx-auto w-full max-w-[min(100%,calc(100vh-14rem))] rounded-md ${phase === "bad" ? "flash-bad animate-shake" : ""} ${phase === "good" ? "flash-good" : ""}`}>
        <Board
          fen={fen}
          orientation={item?.color ?? "white"}
          movable={phase === "answer" ? item?.color : undefined}
          dests={toDests(chess.current)}
          lastMove={lastMove}
          shapes={shapes}
          onMove={onMove}
        />
      </div>
      <aside className="space-y-4">
        <div className="card space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-bold">¿Qué juegas aquí?</h2>
            <span className="text-sm">
              <span className="text-good">{count.good} ✓</span> · <span className="text-bad">{count.bad} ✗</span>
            </span>
          </div>
          <p className="text-sm text-muted">
            {phase === "replay" && "Mira la línea…"}
            {phase === "answer" && `Juegas con ${item?.color === "white" ? "blancas" : "negras"}. Haz la jugada de tu repertorio.`}
            {phase === "good" && "¡Correcto!"}
            {phase === "bad" && `Tu repertorio dice ${item?.san}.`}
          </p>
          {item?.comment && (phase === "good" || phase === "bad") && (
            <p className="rounded-xl bg-panel2 p-2 text-sm">📝 {item.comment}</p>
          )}
          {phase === "bad" && (
            <button className="btn-primary w-full" onClick={next}>
              Siguiente
            </button>
          )}
        </div>
      </aside>
    </div>
  );
}

// --- Desviaciones ------------------------------------------------------------

function Deviations({ onOpen }: { onOpen: (color: Color, path: string[]) => void }) {
  const [rows, setRows] = useState<Deviation[] | null>(null);
  useEffect(() => {
    api<Deviation[]>("/openings/deviations").then(setRows);
  }, []);
  if (!rows) return <p className="text-muted">Analizando tus partidas…</p>;
  if (!rows.length) return <p className="text-muted">Aún no hay partidas.</p>;
  return (
    <div className="card p-0">
      <ul className="divide-y divide-line">
        {rows.map((r) => {
          const d = r.deviation;
          const move = d ? `${Math.ceil(d.ply / 2)}${d.ply % 2 ? "." : "…"}` : "";
          return (
            <li key={r.game_id} className="flex flex-wrap items-center gap-3 px-4 py-3">
              <div className="min-w-0 flex-1">
                <div className="truncate font-semibold">{r.opening?.name ?? "Apertura desconocida"}</div>
                <div className="text-sm text-muted">
                  {!d && "Sin repertorio para esta partida o la seguiste entera."}
                  {d?.type === "you" && (
                    <>
                      <span className="text-bad">Te saliste:</span> jugaste {move} {d.san}; tu repertorio dice {d.expected?.join(" / ")}.
                    </>
                  )}
                  {d?.type === "opponent" && (
                    <>
                      <span className="text-tactics">Tu rival se salió:</span> {move} {d.san} no está preparado.
                    </>
                  )}
                  {d?.type === "end" && <>Seguiste tu repertorio hasta el final de tu preparación ✓</>}
                </div>
              </div>
              {d?.type === "opponent" && d.path && (
                <button className="btn-ghost text-sm" onClick={() => onOpen(r.user_color, d.path!)}>
                  Preparar respuesta
                </button>
              )}
              <Link className="text-sm underline" to={`/revision/${r.game_id}`}>
                Ver partida
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
