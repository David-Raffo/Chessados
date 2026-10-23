import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Chess } from "chess.js";
import confetti from "canvas-confetti";
import Board, { toDests, type Color, type DrawShape, type Key } from "../components/Board";
import Promotion from "../components/Promotion";
import { api } from "../lib/api";
import { themeLabel } from "../lib/labels";
import { sound } from "../lib/sound";
import type { Puzzle } from "../lib/types";
import { useActivity } from "../lib/useActivity";
import { usePuzzle } from "../lib/usePuzzle";

// --- Datos de la API (backend/app/learn.py) ---------------------------------

type Brush = "green" | "red" | "blue" | "yellow";

interface StepBase {
  title?: string;
  text: string;
  fen?: string;
  orientation?: Color;
  arrows?: [string, string, Brush][];
  squares?: Record<string, Brush>;
}
interface ExplainStep extends StepBase {
  type: "explain";
  fen: string;
  moves?: { san: string; text: string }[];
}
interface SelectStep extends StepBase {
  type: "select";
  fen: string;
  answer: string;
  wrong?: Record<string, string>;
  success: string;
}
interface MoveStep extends StepBase {
  type: "move";
  fen: string;
  line: string[];
  hint: string;
  success: string;
}
interface ChoiceStep extends StepBase {
  type: "choice";
  fen: string;
  options: { text: string; correct: boolean; why: string }[];
}
interface PracticeStep extends StepBase {
  type: "practice";
  theme: string;
  count: number;
}
type Step = ExplainStep | SelectStep | MoveStep | ChoiceStep | PracticeStep;

interface LessonProgress {
  step: number;
  completed: boolean;
}
interface Lesson {
  id: string;
  title: string;
  summary: string;
  course_title: string;
  theme?: string;
  steps: Step[];
  progress: LessonProgress;
}
interface Course {
  id: string;
  title: string;
  description: string;
  lessons: { id: string | null; title: string; available: boolean; summary: string | null; minutes: number | null; progress: LessonProgress | null }[];
}

// --- Utilidades -------------------------------------------------------------

/** SAN en notación española: C caballo, A alfil, T torre, D dama, R rey. */
const PIECE_ES: Record<string, string> = { K: "R", Q: "D", R: "T", B: "A", N: "C" };
const sanEs = (san: string) => san.replace(/[KQRBN]/g, (p) => PIECE_ES[p]);
const sameSan = (a: string, b: string) => a.replace(/[+#]/g, "") === b.replace(/[+#]/g, "");

function stepShapes(step: StepBase): DrawShape[] {
  const out: DrawShape[] = [];
  for (const [orig, dest, brush] of step.arrows ?? []) out.push({ orig: orig as Key, dest: dest as Key, brush });
  for (const [sq, brush] of Object.entries(step.squares ?? {})) out.push({ orig: sq as Key, brush });
  return out;
}

// --- Página -------------------------------------------------------------------

export default function Learn() {
  const { id } = useParams();
  return id ? <LessonPlayer key={id} id={id} /> : <Courses />;
}

function Courses() {
  const [courses, setCourses] = useState<Course[] | null>(null);
  useEffect(() => {
    api<{ courses: Course[] }>("/learn").then((r) => setCourses(r.courses));
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-extrabold">Aprender</h1>
        <p className="text-muted">Lecciones cortas con el tablero delante: la idea, ejemplos y a practicar.</p>
      </header>
      {!courses && <p className="text-muted">Cargando…</p>}
      {courses?.map((c) => (
        <section key={c.id} className="space-y-3">
          <div>
            <h2 className="text-lg font-bold">{c.title}</h2>
            <p className="text-sm text-muted">{c.description}</p>
          </div>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {c.lessons.map((l, i) =>
              l.available && l.id ? (
                <Link key={i} to={`/aprender/${l.id}`} className="card flex flex-col gap-1 transition hover:bg-panel2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-semibold">{l.title}</span>
                    {l.progress?.completed ? (
                      <span className="shrink-0 rounded-full bg-good/15 px-2 py-0.5 text-xs font-semibold text-good">✓ Hecha</span>
                    ) : (
                      <span className="shrink-0 text-xs text-muted">{l.minutes} min</span>
                    )}
                  </div>
                  <span className="text-sm text-muted">{l.summary}</span>
                  {!l.progress?.completed && (l.progress?.step ?? 0) > 0 && <span className="text-xs text-tactics">A medias: sigue donde lo dejaste</span>}
                </Link>
              ) : (
                <div key={i} className="flex items-center justify-between gap-2 rounded-2xl border border-dashed border-line p-4 text-muted">
                  <span>{l.title}</span>
                  <span className="text-xs">Próximamente</span>
                </div>
              ),
            )}
          </div>
        </section>
      ))}
    </div>
  );
}

function LessonPlayer({ id }: { id: string }) {
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [error, setError] = useState("");
  const [index, setIndex] = useState(0);
  const [mistakes, setMistakes] = useState(0);
  const [result, setResult] = useState<LessonProgress | null>(null);
  useActivity("tactics", "learn", id);

  useEffect(() => {
    api<Lesson>(`/learn/${id}`)
      .then((l) => {
        setLesson(l);
        // Se retoma donde lo dejaste (si ya la completaste, empieza de nuevo)
        setIndex(l.progress.completed ? 0 : Math.min(l.progress.step, l.steps.length - 1));
      })
      .catch((e) => setError(e.message));
  }, [id]);

  const addMistake = useCallback(() => setMistakes((m) => m + 1), []);

  function next() {
    if (!lesson) return;
    if (index + 1 >= lesson.steps.length) {
      api<LessonProgress>(`/learn/${id}/progress`, { body: { step: lesson.steps.length, completed: true, mistakes } })
        .then(setResult)
        .catch(() => setResult({ step: 0, completed: true }));
      confetti({ particleCount: 90, spread: 70, origin: { y: 0.6 }, disableForReducedMotion: true });
      return;
    }
    setIndex(index + 1);
    api(`/learn/${id}/progress`, { body: { step: index + 1 } }).catch(() => undefined);
    window.scrollTo({ top: 0 });
  }

  if (error) return <p className="text-bad">{error}</p>;
  if (!lesson) return <p className="text-muted">Cargando…</p>;

  const step = lesson.steps[index];
  const header = (
    <header className="space-y-2">
      <Link to="/aprender" className="hidden text-sm text-muted hover:text-fg lg:block">
        ← {lesson.course_title}
      </Link>
      <div className="flex items-baseline justify-between gap-3">
        <h1 className="text-xl font-extrabold">
          <Link to="/aprender" className="mr-1 text-muted hover:text-fg lg:hidden" aria-label="Volver a Aprender">
            ←
          </Link>
          {lesson.title}
        </h1>
        <span className="shrink-0 text-sm text-muted">
          {result ? lesson.steps.length : index + 1} / {lesson.steps.length}
        </span>
      </div>
      <div className="flex gap-1" aria-hidden>
        {lesson.steps.map((_, i) => (
          <span key={i} className={`h-1.5 flex-1 rounded-full ${result || i < index ? "bg-good" : i === index ? "bg-tactics" : "bg-panel2"}`} />
        ))}
      </div>
    </header>
  );

  if (result) {
    return (
      <div className="mx-auto max-w-xl space-y-4">
        {header}
        <div className="card space-y-3 text-center">
          <p className="text-4xl text-good" aria-hidden>
            ✓
          </p>
          <p className="text-2xl font-extrabold">¡Lección completada!</p>
          <p className="text-sm text-muted">Queda marcada como hecha. Puedes repetirla cuando quieras.</p>
          <div className="flex flex-col gap-2 sm:flex-row">
            {lesson.theme && (
              <Link className="btn-primary flex-1" to={`/puzzles?theme=${lesson.theme}`}>
                Más puzzles: {themeLabel(lesson.theme)}
              </Link>
            )}
            <button
              className="btn-ghost flex-1"
              onClick={() => {
                setResult(null);
                setMistakes(0);
                setIndex(0);
              }}
            >
              Repetir
            </button>
            <button className="btn-ghost flex-1" onClick={() => navigate("/aprender")}>
              Volver a Aprender
            </button>
          </div>
        </div>
      </div>
    );
  }

  const props = { header, onNext: next, onMistake: addMistake };
  switch (step.type) {
    case "explain":
      return <Explain key={index} step={step} {...props} />;
    case "select":
      return <Select key={index} step={step} {...props} />;
    case "move":
      return <MoveLine key={index} step={step} {...props} />;
    case "choice":
      return <Choice key={index} step={step} {...props} />;
    case "practice":
      return <Practice key={index} step={step} {...props} />;
  }
}

interface StepProps<S> {
  step: S;
  header: ReactNode;
  onNext: () => void;
  onMistake: () => void;
}

/** Tablero y panel: en móvil, cabecera arriba, tablero centrado y el texto justo debajo. */
function StepLayout({
  header,
  board,
  overlay,
  flash,
  children,
}: {
  header: ReactNode;
  board: ReactNode;
  overlay?: ReactNode;
  flash?: "good" | "bad" | null;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-6">
      <div className="lg:hidden">{header}</div>
      <div className="mx-auto w-full max-w-[min(100%,calc(100vh-10rem))]">
        <div className={`relative rounded-md ${flash === "bad" ? "flash-bad animate-shake" : ""} ${flash === "good" ? "flash-good" : ""}`}>
          {board}
          {overlay}
        </div>
      </div>
      <aside className="space-y-4">
        <div className="hidden lg:block">{header}</div>
        <div className="card space-y-3">{children}</div>
      </aside>
    </div>
  );
}

function StepText({ step }: { step: StepBase }) {
  return (
    <>
      {step.title && <h2 className="font-bold">{step.title}</h2>}
      <p className="leading-relaxed">{step.text}</p>
    </>
  );
}

function Feedback({ kind, children }: { kind: "good" | "bad" | "info"; children: ReactNode }) {
  const cls = kind === "good" ? "bg-good/15 text-good" : kind === "bad" ? "bg-bad/15 text-bad" : "bg-panel2";
  return <div className={`rounded-xl p-3 text-sm font-medium ${cls}`}>{children}</div>;
}

function useFlash() {
  const [flash, setFlash] = useState<"good" | "bad" | null>(null);
  const timer = useRef<number>();
  const show = useCallback((f: "good" | "bad") => {
    setFlash(f);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setFlash(null), f === "bad" ? 400 : 900);
  }, []);
  useEffect(() => () => window.clearTimeout(timer.current), []);
  return [flash, show] as const;
}

// --- Explicación --------------------------------------------------------------

function Explain({ step, header, onNext }: StepProps<ExplainStep>) {
  const moves = step.moves ?? [];
  const [ply, setPly] = useState(0);
  const pos = useMemo(() => {
    const c = new Chess(step.fen);
    let last: Key[] | undefined;
    for (const m of moves.slice(0, ply)) {
      const mv = c.move(m.san);
      last = [mv.from as Key, mv.to as Key];
    }
    return { fen: c.fen(), last, check: c.inCheck() };
  }, [step.fen, moves, ply]);
  const done = ply >= moves.length;

  return (
    <StepLayout
      header={header}
      board={<Board fen={pos.fen} orientation={step.orientation ?? "white"} lastMove={pos.last} check={pos.check} shapes={ply === 0 ? stepShapes(step) : undefined} />}
    >
      {/* Al avanzar, el comentario de la jugada sustituye al texto inicial: así los botones quedan
          cerca del tablero en el móvil */}
      {ply === 0 ? <StepText step={step} /> : step.title && <h2 className="font-bold">{step.title}</h2>}
      {moves.length > 0 && (
        <>
          {ply > 0 && (
            <Feedback kind="info">
              <b>{sanEs(moves[ply - 1].san)}</b> · {moves[ply - 1].text}
            </Feedback>
          )}
          <div className="flex gap-2">
            <button className="btn-ghost flex-1" disabled={ply === 0} onClick={() => setPly(0)} aria-label="Al principio">
              ⏮
            </button>
            <button className="btn-ghost flex-1" disabled={ply === 0} onClick={() => setPly(ply - 1)} aria-label="Anterior">
              ◀
            </button>
            <button className="btn-ghost flex-1" disabled={done} onClick={() => setPly(ply + 1)} aria-label="Siguiente jugada">
              ▶
            </button>
          </div>
        </>
      )}
      {done ? (
        <button className="btn-primary w-full" onClick={onNext}>
          Continuar
        </button>
      ) : (
        <p className="text-center text-sm text-muted">{ply === 0 ? "Pulsa ▶ para ver la primera jugada." : `Jugada ${ply} de ${moves.length}`}</p>
      )}
    </StepLayout>
  );
}

// --- Señalar una casilla --------------------------------------------------------

function Select({ step, header, onNext, onMistake }: StepProps<SelectStep>) {
  const [solved, setSolved] = useState(false);
  const [wrong, setWrong] = useState<{ key: string; text: string } | null>(null);
  const tried = useRef(new Set<string>());
  const [flash, showFlash] = useFlash();

  function onSelect(key: Key) {
    if (solved) return;
    if (key === step.answer) {
      setSolved(true);
      setWrong(null);
      sound.good();
      showFlash("good");
      return;
    }
    sound.bad();
    showFlash("bad");
    if (!tried.current.has(key)) {
      tried.current.add(key);
      onMistake();
    }
    setWrong({ key, text: step.wrong?.[key] ?? "No es esa casilla. Prueba otra." });
  }

  const shapes: DrawShape[] = [...stepShapes(step)];
  if (solved) shapes.push({ orig: step.answer as Key, brush: "green" });
  else if (wrong) shapes.push({ orig: wrong.key as Key, brush: "red" });

  return (
    <StepLayout header={header} flash={flash} board={<Board fen={step.fen} orientation={step.orientation ?? "white"} shapes={shapes} onSelect={onSelect} />}>
      <StepText step={step} />
      {solved ? <Feedback kind="good">{step.success}</Feedback> : wrong && <Feedback kind="bad">{wrong.text}</Feedback>}
      {solved && (
        <button className="btn-primary w-full" onClick={onNext}>
          Continuar
        </button>
      )}
    </StepLayout>
  );
}

// --- Jugar una línea --------------------------------------------------------------

function MoveLine({ step, header, onNext, onMistake }: StepProps<MoveStep>) {
  const chess = useRef(new Chess(step.fen));
  const [fen, setFen] = useState(step.fen);
  const [idx, setIdx] = useState(0); // siguiente jugada de `line`
  const [last, setLast] = useState<Key[] | undefined>();
  const [solved, setSolved] = useState(false);
  const [waiting, setWaiting] = useState(false);
  const [fails, setFails] = useState(0);
  const [note, setNote] = useState("");
  const [flash, showFlash] = useFlash();
  const userColor: Color = step.fen.split(" ")[1] === "w" ? "white" : "black";
  const timer = useRef<number>();
  useEffect(() => () => window.clearTimeout(timer.current), []);

  // Tras el primer fallo se marca la pieza que hay que mover
  const hintFrom = useMemo(() => {
    if (!fails || solved || idx >= step.line.length) return null;
    try {
      return new Chess(fen).move(step.line[idx]).from as Key;
    } catch {
      return null;
    }
  }, [fails, solved, idx, fen, step.line]);

  function onMove(from: Key, to: Key) {
    if (solved || waiting) return;
    const c = chess.current;
    let mv;
    try {
      mv = c.move({ from, to, promotion: "q" });
    } catch {
      return;
    }
    const ok = sameSan(mv.san, step.line[idx]) || c.isCheckmate();
    if (!ok) {
      c.undo();
      setFen(c.fen());
      setFails((f) => f + 1);
      setNote(`${sanEs(mv.san)} no es la jugada.`);
      onMistake();
      sound.bad();
      showFlash("bad");
      return;
    }
    setFen(c.fen());
    setLast([from, to]);
    setNote("");
    if (mv.captured) sound.capture();
    else sound.move();
    if (c.isCheckmate() || idx + 1 >= step.line.length) {
      setSolved(true);
      setIdx(step.line.length);
      sound.good();
      showFlash("good");
      return;
    }
    // Respuesta del rival
    setWaiting(true);
    timer.current = window.setTimeout(() => {
      const reply = c.move(step.line[idx + 1]);
      setFen(c.fen());
      setLast([reply.from as Key, reply.to as Key]);
      if (c.inCheck()) sound.check();
      else if (reply.captured) sound.capture();
      else sound.move();
      setIdx(idx + 2);
      setWaiting(false);
    }, 550);
  }

  const shapes: DrawShape[] = idx === 0 && !fails ? stepShapes(step) : hintFrom ? [{ orig: hintFrom, brush: "yellow" }] : [];
  const yourTurn = !solved && !waiting;

  return (
    <StepLayout
      header={header}
      flash={flash}
      board={
        <Board
          fen={fen}
          orientation={step.orientation ?? userColor}
          movable={yourTurn ? userColor : undefined}
          dests={yourTurn ? toDests(chess.current) : undefined}
          lastMove={last}
          check={chess.current.inCheck()}
          shapes={shapes}
          onMove={onMove}
        />
      }
    >
      <StepText step={step} />
      {solved ? (
        <Feedback kind="good">{step.success}</Feedback>
      ) : note ? (
        <Feedback kind="bad">
          {note} <span className="font-normal">{step.hint}</span>
        </Feedback>
      ) : (
        <Feedback kind="info">{waiting ? "Responde el rival…" : `Juegan las ${userColor === "white" ? "blancas" : "negras"}.`}</Feedback>
      )}
      {solved && (
        <button className="btn-primary w-full" onClick={onNext}>
          Continuar
        </button>
      )}
    </StepLayout>
  );
}

// --- Elegir una opción ----------------------------------------------------------------

function Choice({ step, header, onNext, onMistake }: StepProps<ChoiceStep>) {
  const [picked, setPicked] = useState<number[]>([]);
  const last = picked.length ? step.options[picked[picked.length - 1]] : null;
  const solved = !!last?.correct;

  function pick(i: number) {
    if (solved || picked.includes(i)) return;
    setPicked([...picked, i]);
    if (step.options[i].correct) sound.good();
    else {
      sound.bad();
      onMistake();
    }
  }

  return (
    <StepLayout header={header} board={<Board fen={step.fen} orientation={step.orientation ?? "white"} shapes={stepShapes(step)} />}>
      <StepText step={step} />
      <div className="flex flex-col gap-2">
        {step.options.map((o, i) => {
          const tried = picked.includes(i);
          const cls = tried ? (o.correct ? "border-good bg-good/15 text-good" : "border-bad bg-bad/10 text-muted line-through") : "border-line hover:bg-panel2";
          return (
            <button key={i} disabled={solved || tried} onClick={() => pick(i)} className={`rounded-xl border p-3 text-left font-medium transition ${cls}`}>
              {tried && o.correct && "✓ "}
              {o.text}
            </button>
          );
        })}
      </div>
      {last && <Feedback kind={last.correct ? "good" : "bad"}>{last.why}</Feedback>}
      {solved && (
        <button className="btn-primary w-full" onClick={onNext}>
          Continuar
        </button>
      )}
    </StepLayout>
  );
}

// --- Práctica con puzzles reales -------------------------------------------------------

function Practice({ step, header, onNext }: StepProps<PracticeStep>) {
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null);
  const [results, setResults] = useState<boolean[]>([]);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    api<Puzzle>(`/puzzles/next?theme=${step.theme}&area=tactics`)
      .then(setPuzzle)
      .catch((e) => setError(e.message));
  }, [step.theme]);
  useEffect(load, [load]);

  const p = usePuzzle(puzzle, {
    onDone: (solved, seconds) => {
      if (!puzzle) return;
      setResults((r) => [...r, solved]);
      // Cuenta como un puzzle normal: mueve tu ELO de táctica
      api(`/puzzles/${puzzle.id}/attempt`, { body: { solved, seconds, mode: "normal", area: "tactics" } }).catch(() => undefined);
    },
  });
  const finishedPuzzle = p.status === "solved" || p.status === "failed";
  const allDone = results.length >= step.count && finishedPuzzle;

  return (
    <StepLayout
      header={header}
      flash={p.flash}
      board={
        <Board
          fen={p.fen}
          orientation={p.color}
          movable={p.status === "play" && p.turn === p.color ? p.color : undefined}
          dests={p.dests}
          lastMove={p.lastMove}
          check={p.check}
          onMove={(f, t) => p.userMove(f, t)}
        />
      }
      overlay={
        p.promo && (
          <Promotion
            color={p.color}
            onPick={(role) => {
              const m = p.promo!;
              p.setPromo(null);
              p.userMove(m.from, m.to, role);
            }}
            onCancel={p.resetPromo}
          />
        )
      }
    >
      <StepText step={step} />
      <div className="flex items-center gap-1.5" aria-label={`${results.length} de ${step.count}`}>
        {Array.from({ length: step.count }, (_, i) => (
          <span key={i} className={`h-2.5 flex-1 rounded-full ${i < results.length ? (results[i] ? "bg-good" : "bg-bad") : "bg-panel2"}`} />
        ))}
      </div>
      {error ? (
        <Feedback kind="bad">{error}</Feedback>
      ) : (
        <Feedback kind={p.status === "solved" ? "good" : p.status === "failed" ? "bad" : "info"}>
          {p.status === "intro" && "Mira la jugada del rival…"}
          {p.status === "play" && (p.wrong ? "No es eso. Sigue intentándolo." : `Juegan las ${p.color === "white" ? "blancas" : "negras"}: busca el ${themeLabel(step.theme).toLowerCase()}.`)}
          {p.status === "solved" && "¡Correcto!"}
          {p.status === "failed" && (p.recovered ? "Resuelto, pero cuenta como fallado." : "Fallado.")}
        </Feedback>
      )}
      {p.status === "play" && (
        <button className="btn-ghost w-full" onClick={p.showSolution}>
          Ver solución
        </button>
      )}
      {(allDone || error) && (
        <button className="btn-primary w-full" onClick={onNext}>
          Terminar la lección
        </button>
      )}
      {finishedPuzzle && !allDone && !error && (
        <button className="btn-primary w-full" onClick={load}>
          Siguiente puzzle ({results.length + 1} de {step.count})
        </button>
      )}
    </StepLayout>
  );
}
