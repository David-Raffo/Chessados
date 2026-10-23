import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Ring from "../components/Ring";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { AREA_BG, AREA_COLOR_VAR, AREA_LABEL, AREA_TEXT, formatDuration, themeLabel } from "../lib/labels";
import { setActiveStep, stepLink } from "../lib/plan";
import type { Area, CoachPlan, PlanStep, RatingArea } from "../lib/types";

interface Overview {
  ratings: Record<RatingArea, { rating: number; rd: number; provisional: boolean }>;
  streak: number;
  today_seconds: number;
  week: Record<Area, number>;
  week_target: Record<Area, number>;
}

const stepKey = (s: PlanStep, i: number) => `${i}-${s.kind}-${s.area}`;

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [plan, setPlan] = useState<CoachPlan | null>(null);
  const [puzzleCount, setPuzzleCount] = useState<number | null>(null);

  useEffect(() => {
    api<Overview>("/stats/overview").then(setOverview).catch(() => undefined);
    api<CoachPlan>("/coach/today").then(setPlan).catch(() => undefined);
    api<{ count: number }>("/puzzles/count").then((r) => setPuzzleCount(r.count)).catch(() => undefined);
  }, []);

  // Un paso solo cuenta como hecho cuando el servidor ve la actividad real (tiempo, partida, revisión…)
  const go = (step: PlanStep, i: number) => {
    setActiveStep(i); // activa la barra de «Entrenamiento en curso» en el resto de pantallas
    navigate(stepLink(step));
  };
  // Las sugerencias extra son libres: no activan la barra de la sesión
  const goExtra = (step: PlanStep) => {
    setActiveStep(null);
    navigate(stepLink(step));
  };
  const extras = plan?.extras ?? [];
  const nextIndex = plan ? plan.steps.findIndex((s) => !s.done) : -1;
  const started = !!plan?.steps.some((s) => (s.progress ?? 0) > 0);
  const finished = !!plan && nextIndex === -1;
  const hour = new Date().getHours();
  const greeting = hour < 14 ? "Buenos días" : hour < 21 ? "Buenas tardes" : "Buenas noches";

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-muted">{greeting},</p>
          <h1 className="text-3xl font-extrabold">{user?.name}</h1>
        </div>
        <div className="flex gap-3">
          <div className="card flex items-center gap-2 px-4 py-2">
            <span className="text-2xl">🔥</span>
            <div>
              <div className="text-xl font-extrabold leading-none">{overview?.streak ?? "–"}</div>
              <div className="text-xs text-muted">días de racha</div>
            </div>
          </div>
          <div className="card px-4 py-2">
            <div className="text-xl font-extrabold leading-none">{formatDuration(overview?.today_seconds ?? 0)}</div>
            <div className="text-xs text-muted">hoy</div>
          </div>
        </div>
      </header>

      {puzzleCount === 0 && (
        <div className="card border-tactics/50 bg-tactics/10 text-sm">
          Los puzzles de Lichess todavía se están importando. Tardará unos minutos la primera vez.
        </div>
      )}

      <section className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        <div className="card space-y-4 p-4 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold">Sesión de hoy</h2>
              <p className="text-sm text-muted">
                {plan ? `${plan.steps.reduce((a, s) => a + s.minutes, 0)} minutos según tus objetivos y tus errores` : "Preparando…"}
              </p>
            </div>
          </div>
          <button
            className="btn-primary w-full py-3 text-lg sm:py-4 sm:text-xl"
            disabled={!plan}
            onClick={() => {
              if (!plan) return;
              if (finished) {
                if (extras[0]) goExtra(extras[0]);
                return;
              }
              go(plan.steps[nextIndex], nextIndex);
            }}
          >
            {finished ? "Seguir entrenando" : started ? "Continuar entrenamiento" : "Entrenar hoy"} →
          </button>
          {finished && (
            <div className="space-y-2 rounded-xl border border-good/40 bg-good/10 p-4">
              <p className="font-semibold text-good">🎉 ¡Sesión de hoy completada!</p>
              {extras.length > 0 && (
                <>
                  <p className="text-sm text-muted">Si te apetece seguir, tu entrenador te sugiere:</p>
                  <ul className="space-y-2">
                    {extras.map((x, i) => (
                      <li key={i}>
                        <button
                          onClick={() => goExtra(x)}
                          className="flex w-full items-center gap-3 rounded-xl border border-line bg-panel p-3 text-left transition hover:bg-panel2"
                        >
                          <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${AREA_BG[x.area]}`} />
                          <span className="min-w-0 flex-1">
                            <span className="block font-medium">
                              {x.title}
                              {x.theme && x.theme !== "endgame" && <span className="text-muted"> · {themeLabel(x.theme)}</span>}
                            </span>
                            {x.reason && <span className="block text-sm text-muted">{x.reason}</span>}
                          </span>
                          <span className="shrink-0 text-sm text-muted">{x.minutes} min</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          )}
          <ol className="space-y-2">
            {plan?.steps.map((s, i) => {
              const isDone = !!s.done;
              return (
                <li key={stepKey(s, i)}>
                  <button
                    onClick={() => go(s, i)}
                    className={`flex w-full items-center gap-3 rounded-xl border border-line p-3 text-left transition hover:bg-panel2 ${
                      i === nextIndex ? "ring-2 ring-fg/20" : ""
                    }`}
                  >
                    <span
                      className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-bold text-bg ${
                        isDone ? "bg-good" : AREA_BG[s.area]
                      }`}
                    >
                      {isDone ? "✓" : i + 1}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className={`block font-medium ${isDone ? "text-muted line-through" : ""}`}>
                        {s.title}
                        {s.theme && s.theme !== "endgame" && <span className="text-muted"> · {themeLabel(s.theme)}</span>}
                      </span>
                      {/* En móvil el estado va debajo del título para que el título no se parta palabra a palabra */}
                      <span className="mt-0.5 block text-sm text-muted sm:hidden">{s.status ?? `${s.minutes} min`}</span>
                      {!isDone && (s.progress ?? 0) > 0 && (
                        <span className="mt-1 block h-1 overflow-hidden rounded-full bg-panel2">
                          <span className="block h-full" style={{ width: `${(s.progress ?? 0) * 100}%`, background: AREA_COLOR_VAR[s.area] }} />
                        </span>
                      )}
                    </span>
                    <span className="hidden max-w-[45%] shrink-0 text-right text-sm text-muted sm:block">{s.status ?? `${s.minutes} min`}</span>
                  </button>
                </li>
              );
            })}
          </ol>
        </div>

        <div className="space-y-6">
          <div className="card space-y-3">
            <h2 className="font-bold">Tu entrenador dice</h2>
            {plan?.advice.map((a, i) => (
              <div key={i} className={`flex gap-3 ${i === 0 ? "" : "text-sm"}`}>
                <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${AREA_BG[a.area] ?? "bg-muted"}`} />
                <p className={i === 0 ? "font-medium" : "text-muted"}>
                  {a.text}{" "}
                  {a.rule === 2 && a.theme && (
                    <Link className="underline" to={`/puzzles?theme=${a.theme}`}>
                      Empezar
                    </Link>
                  )}
                  {a.rule === 4 && a.game_id && (
                    <Link className="underline" to={`/revision/${a.game_id}`}>
                      Revisar
                    </Link>
                  )}
                  {a.link && (
                    <Link className="underline" to={a.link}>
                      Ir
                    </Link>
                  )}
                </p>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="mb-3 flex items-baseline justify-between">
              <h2 className="font-bold">Esta semana</h2>
              <span className="text-sm text-muted">objetivo {user?.weekly_hours} h</span>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {(["tactics", "play", "endgames", "openings"] as Area[]).map((a) => (
                <div key={a} className="flex flex-col items-center gap-1">
                  <Ring
                    value={overview?.week[a] ?? 0}
                    max={overview?.week_target[a] ?? 1}
                    color={AREA_COLOR_VAR[a]}
                    size={72}
                    stroke={8}
                  >
                    <span className="text-xs font-bold">
                      {overview && overview.week_target[a]
                        ? `${Math.round((100 * overview.week[a]) / overview.week_target[a])}%`
                        : "–"}
                    </span>
                  </Ring>
                  <span className={`text-xs font-semibold ${AREA_TEXT[a]}`}>{AREA_LABEL[a]}</span>
                  {/* Hecho y objetivo en dos líneas: en una sola se partía por la mitad en móvil */}
                  <span className="text-center text-[11px] leading-tight text-muted">
                    <span className="block whitespace-nowrap">{formatDuration(overview?.week[a] ?? 0)}</span>
                    <span className="block whitespace-nowrap">de {formatDuration(overview?.week_target[a] ?? 0)}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {(["tactics", "play", "endgames", "rush"] as RatingArea[]).map((a) => {
          const r = overview?.ratings[a];
          return (
            <Link key={a} to="/progreso" className="card transition hover:bg-panel2">
              <div className={`text-sm font-semibold ${AREA_TEXT[a]}`}>{AREA_LABEL[a]}</div>
              <div className="text-3xl font-extrabold">
                {r?.rating ?? "–"}
                {r?.provisional && <span className="text-lg text-muted">?</span>}
              </div>
              <div className="text-xs text-muted">ELO Glicko-2</div>
            </Link>
          );
        })}
      </section>
    </div>
  );
}
