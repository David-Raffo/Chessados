import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { AREA_COLOR_VAR } from "../lib/labels";
import { onLiveTick, onSynced, unsentFor } from "../lib/live";
import { TIMED, getActiveStep, onActiveStepChange, setActiveStep, stepLink } from "../lib/plan";
import type { CoachPlan, PlanStep } from "../lib/types";

const mmss = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

/** Barra fija de «Entrenamiento en curso»: paso actual, tiempo hecho frente al recomendado y siguiente paso. */
export default function PlanBanner() {
  const location = useLocation();
  const navigate = useNavigate();
  const [index, setIndex] = useState<number | null>(getActiveStep());
  const [steps, setSteps] = useState<PlanStep[] | null>(null);
  const [, setTick] = useState(0);
  const shown = useRef<{ index: number | null; seconds: number }>({ index: null, seconds: 0 });

  const refresh = useCallback(() => {
    if (getActiveStep() == null) return;
    api<CoachPlan>("/coach/today").then((p) => setSteps(p.steps)).catch(() => undefined);
  }, []);

  useEffect(() => onActiveStepChange(() => setIndex(getActiveStep())), []);
  useEffect(refresh, [refresh, index, location.pathname]);
  useEffect(() => onSynced(refresh), [refresh]);
  useEffect(() => onLiveTick(() => setTick((t) => t + 1)), []);
  useEffect(() => {
    const id = window.setInterval(refresh, 60_000); // partidas o revisiones terminadas en otra pantalla
    return () => window.clearInterval(id);
  }, [refresh]);

  if (index == null || !steps || !steps[index] || location.pathname === "/") return null;
  const step = steps[index];
  const nextIndex = steps.findIndex((s, i) => i !== index && !s.done);
  const timed = TIMED[step.kind];

  // Tiempo en vivo: lo confirmado por el servidor + lo que aún no se ha enviado (nunca retrocede)
  let seconds = 0;
  let target = 0;
  if (timed && step.target_seconds) {
    target = step.target_seconds;
    const live = (step.seconds ?? 0) + unsentFor(timed.area, timed.activities);
    if (shown.current.index !== index) shown.current = { index, seconds: 0 };
    seconds = Math.max(shown.current.seconds, live);
    shown.current.seconds = seconds;
  }
  const done = step.done || (timed ? seconds >= target : false);
  const pct = timed ? Math.min(100, (100 * seconds) / target) : step.done ? 100 : 0;
  const onStepPage = location.pathname + location.search === stepLink(step) || location.pathname === stepLink(step).split("?")[0];

  function goTo(i: number) {
    setActiveStep(i);
    navigate(stepLink(steps![i]));
  }

  return (
    <div className="sticky top-0 z-20 -mx-4 mb-4 border-b border-line bg-panel/95 px-4 py-2 backdrop-blur md:-mx-8 md:-mt-8 md:mb-6 md:px-8">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-3 text-sm">
            <span className="truncate">
              <span className="text-muted">Entrenamiento · paso {index + 1} de {steps.length}:</span>{" "}
              <span className="font-semibold">{step.title}</span>
            </span>
            <span className="shrink-0 font-mono font-bold tabular-nums">
              {timed ? (
                <>
                  {mmss(seconds)} <span className="font-normal text-muted">/ {mmss(target)}</span>
                </>
              ) : (
                <span className="font-sans text-muted">{step.status}</span>
              )}
            </span>
          </div>
          <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-panel2">
            <div
              className="h-full transition-all duration-700"
              style={{ width: `${pct}%`, background: done ? "rgb(var(--good))" : AREA_COLOR_VAR[step.area] }}
            />
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2 text-sm">
          {done ? (
            nextIndex >= 0 ? (
              <button className="btn-primary px-3 py-1.5" onClick={() => goTo(nextIndex)}>
                ✓ Siguiente: {steps[nextIndex].title} →
              </button>
            ) : (
              <Link className="btn-primary px-3 py-1.5" to="/" onClick={() => setActiveStep(null)}>
                ✓ ¡Sesión completada!
              </Link>
            )
          ) : (
            !onStepPage && (
              <Link className="btn-ghost px-3 py-1.5" to={stepLink(step)}>
                Volver al paso
              </Link>
            )
          )}
          <button className="px-2 text-muted hover:text-fg" title="Salir del entrenamiento" onClick={() => setActiveStep(null)}>
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}
