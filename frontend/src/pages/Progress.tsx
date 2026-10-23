import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../lib/api";
import { AREA_COLOR_VAR, AREA_LABEL, PHASE_LABEL, formatDuration, themeLabel } from "../lib/labels";
import type { Area, RatingArea } from "../lib/types";

interface ProgressData {
  rating_history: Record<RatingArea, { date: string; rating: number }[]>;
  heatmap: { date: string; seconds: number }[];
  weeks: ({ week: string } & Record<Area, number>)[];
  week: Record<Area, number>;
  week_target: Record<Area, number>;
  themes: { theme: string; attempts: number; accuracy: number; avg_seconds: number }[];
  weak_themes: { theme: string; attempts: number; accuracy: number; avg_seconds: number }[];
  errors: { by_phase: Record<string, { mistake: number; blunder: number }>; by_type: Record<string, number> };
}

const tooltipStyle = {
  contentStyle: { background: "rgb(var(--panel))", border: "1px solid rgb(var(--line))", borderRadius: 12 },
};
const axis = { stroke: "rgb(var(--muted))", fontSize: 12 };
const AREAS: Area[] = ["tactics", "play", "endgames", "openings"];
const RATING_AREAS: RatingArea[] = ["tactics", "play", "endgames", "rush"];

export default function Progress() {
  const [data, setData] = useState<ProgressData | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  useEffect(() => {
    api<ProgressData>("/stats/progress").then(setData).catch(() => undefined);
    api<Report>("/stats/weekly-report").then(setReport).catch(() => undefined);
  }, []);

  const ratingRows = useMemo(() => {
    if (!data) return [];
    // Una fila por fecha con el último rating conocido de cada área
    const dates = [...new Set(RATING_AREAS.flatMap((a) => data.rating_history[a]?.map((p) => p.date) ?? []))].sort();
    const last: Partial<Record<RatingArea, number>> = {};
    return dates.map((d) => {
      for (const a of RATING_AREAS) {
        const hit = data.rating_history[a]?.find((p) => p.date === d);
        if (hit) last[a] = hit.rating;
      }
      return { date: d.slice(5), ...last };
    });
  }, [data]);

  if (!data) return <p className="text-muted">Cargando progreso…</p>;

  const weekBars = AREAS.map((a) => ({
    area: AREA_LABEL[a],
    real: +(data.week[a] / 3600).toFixed(2),
    objetivo: +(data.week_target[a] / 3600).toFixed(2),
    color: AREA_COLOR_VAR[a],
  }));
  const radar = data.themes
    .filter((t) => !["short", "long", "veryLong", "oneMove", "middlegame", "opening", "endgame", "crushing", "advantage", "mate", "master", "equality"].includes(t.theme))
    .slice(0, 8)
    .map((t) => ({ theme: themeLabel(t.theme), accuracy: t.accuracy }));
  const phases = Object.entries(data.errors.by_phase).map(([p, v]) => ({
    phase: PHASE_LABEL[p] ?? p,
    Errores: v.mistake,
    Graves: v.blunder,
  }));
  const weeks = data.weeks.map((w) => ({
    week: w.week.slice(5),
    ...Object.fromEntries(AREAS.map((a) => [a, +(w[a] / 3600).toFixed(2)])),
  }));

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-extrabold">Progreso</h1>
        <p className="text-muted">ELO por área, horas frente al objetivo y dónde fallas.</p>
      </header>

      {report && <WeeklyReport report={report} />}

      <section className="card">
        <h2 className="mb-3 font-semibold">Evolución del ELO</h2>
        <div className="h-72">
          <ResponsiveContainer>
            <LineChart data={ratingRows} margin={{ left: -10, right: 8, top: 8 }}>
              <CartesianGrid stroke="rgb(var(--line))" strokeDasharray="3 3" />
              <XAxis dataKey="date" {...axis} />
              <YAxis domain={["auto", "auto"]} {...axis} />
              <Tooltip {...tooltipStyle} />
              <Legend />
              {RATING_AREAS.map((a) => (
                <Line
                  key={a}
                  type="monotone"
                  dataKey={a}
                  name={AREA_LABEL[a]}
                  stroke={AREA_COLOR_VAR[a]}
                  strokeWidth={2.5}
                  dot={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card">
        <h2 className="mb-3 font-semibold">Días entrenados (últimos 6 meses)</h2>
        <Heatmap days={data.heatmap} />
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card">
          <h2 className="mb-3 font-semibold">Esta semana: horas reales frente a objetivo</h2>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={weekBars} margin={{ left: -20, right: 8, top: 8 }}>
                <CartesianGrid stroke="rgb(var(--line))" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="area" {...axis} />
                <YAxis {...axis} unit=" h" />
                <Tooltip {...tooltipStyle} formatter={(v: number) => formatDuration(v * 3600)} />
                <Legend />
                <Bar dataKey="objetivo" name="Objetivo" fill="rgb(var(--line))" radius={[6, 6, 0, 0]} />
                <Bar dataKey="real" name="Real" fill="rgb(var(--play))" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card">
          <h2 className="mb-3 font-semibold">Precisión por tema táctico (90 días)</h2>
          {radar.length >= 3 ? (
            <div className="h-64">
              <ResponsiveContainer>
                <RadarChart data={radar} outerRadius="70%">
                  <PolarGrid stroke="rgb(var(--line))" />
                  <PolarAngleAxis dataKey="theme" tick={{ fill: "rgb(var(--muted))", fontSize: 11 }} />
                  <Radar dataKey="accuracy" name="Acierto %" stroke="rgb(var(--tactics))" fill="rgb(var(--tactics))" fillOpacity={0.35} />
                  <Tooltip {...tooltipStyle} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-muted">Resuelve más puzzles para ver tu radar de temas.</p>
          )}
        </section>

        <section className="card">
          <h2 className="mb-3 font-semibold">Horas por semana</h2>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={weeks} margin={{ left: -20, right: 8, top: 8 }}>
                <CartesianGrid stroke="rgb(var(--line))" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="week" {...axis} />
                <YAxis {...axis} unit=" h" />
                <Tooltip {...tooltipStyle} formatter={(v: number) => formatDuration(v * 3600)} />
                {AREAS.map((a) => (
                  <Bar key={a} dataKey={a} name={AREA_LABEL[a]} stackId="h" fill={AREA_COLOR_VAR[a]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card">
          <h2 className="mb-3 font-semibold">Errores en tus partidas por fase</h2>
          <div className="h-48">
            <ResponsiveContainer>
              <BarChart data={phases} layout="vertical" margin={{ left: 20, right: 8 }}>
                <XAxis type="number" {...axis} allowDecimals={false} />
                <YAxis type="category" dataKey="phase" {...axis} width={90} />
                <Tooltip {...tooltipStyle} />
                <Legend />
                <Bar dataKey="Errores" stackId="e" fill="rgb(var(--rush))" />
                <Bar dataKey="Graves" stackId="e" fill="rgb(var(--bad))" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex flex-wrap gap-2 text-sm">
            {Object.entries(data.errors.by_type).map(([t, n]) => (
              <span key={t} className="rounded-full bg-panel2 px-3 py-1">
                {t}: <b>{n}</b>
              </span>
            ))}
          </div>
        </section>
      </div>

      <section className="card">
        <h2 className="mb-3 font-semibold">Tus temas más débiles</h2>
        {data.weak_themes.length === 0 ? (
          <p className="text-sm text-muted">Ningún tema por debajo de tu media (cuentan los temas con 5 intentos o más en 30 días).</p>
        ) : (
          <ul className="grid gap-2 sm:grid-cols-3">
            {data.weak_themes.map((t) => (
              <li key={t.theme} className="rounded-xl border border-line p-3">
                <div className="font-semibold">{themeLabel(t.theme)}</div>
                <div className="text-sm text-muted">
                  {t.accuracy}% de acierto · {t.avg_seconds}s de media · {t.attempts} intentos
                </div>
                <Link to={`/puzzles?theme=${t.theme}`} className="mt-1 inline-block text-sm underline">
                  Entrenar este tema
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

interface Report {
  week_start: string;
  week: Record<Area, number>;
  week_target: Record<Area, number>;
  elo: Record<RatingArea, { now: number; change: number }>;
  weak_themes: { theme: string; accuracy: number }[];
  tips: string[];
}

function WeeklyReport({ report }: { report: Report }) {
  const total = AREAS.reduce((a, k) => a + report.week[k], 0);
  const target = AREAS.reduce((a, k) => a + report.week_target[k], 0);
  return (
    <section className="card space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-lg font-bold">Informe de la semana</h2>
        <span className="text-sm text-muted">
          desde el {new Date(report.week_start).toLocaleDateString("es-ES", { day: "numeric", month: "long" })}
        </span>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="space-y-2">
          <div className="text-sm font-semibold text-muted">
            Horas: {formatDuration(total)} de {formatDuration(target)}
          </div>
          {AREAS.map((a) => {
            const pct = report.week_target[a] ? Math.min(100, (100 * report.week[a]) / report.week_target[a]) : 0;
            return (
              <div key={a} className="text-sm">
                <div className="flex justify-between">
                  <span>{AREA_LABEL[a]}</span>
                  <span className="text-muted">{Math.round(pct)}%</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-panel2">
                  <div className="h-full" style={{ width: `${pct}%`, background: AREA_COLOR_VAR[a] }} />
                </div>
              </div>
            );
          })}
        </div>
        <div className="space-y-2">
          <div className="text-sm font-semibold text-muted">ELO esta semana</div>
          {RATING_AREAS.map((a) => {
            const e = report.elo[a];
            return (
              <div key={a} className="flex justify-between text-sm">
                <span>{AREA_LABEL[a]}</span>
                <span className="font-semibold">
                  {e.now}{" "}
                  <span className={e.change > 0 ? "text-good" : e.change < 0 ? "text-bad" : "text-muted"}>
                    {e.change > 0 ? `+${e.change}` : e.change || "±0"}
                  </span>
                </span>
              </div>
            );
          })}
          {report.weak_themes.length > 0 && (
            <div className="pt-2 text-sm">
              <span className="text-muted">Temas débiles: </span>
              {report.weak_themes.map((t) => `${themeLabel(t.theme)} (${t.accuracy}%)`).join(", ")}
            </div>
          )}
        </div>
        <div className="space-y-2">
          <div className="text-sm font-semibold text-muted">Consejos</div>
          <ol className="list-decimal space-y-1 pl-5 text-sm">
            {report.tips.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}

function Heatmap({ days }: { days: { date: string; seconds: number }[] }) {
  // Columnas por semana empezando en lunes
  const first = new Date(days[0]?.date ?? Date.now());
  const offset = (first.getDay() + 6) % 7;
  const cells: ({ date: string; seconds: number } | null)[] = [...Array(offset).fill(null), ...days];
  const weeks: (typeof cells)[] = [];
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
  const level = (s: number) => (s <= 0 ? 0 : s < 900 ? 1 : s < 1800 ? 2 : s < 3600 ? 3 : 4);
  const opacity = [0, 0.3, 0.55, 0.8, 1];
  return (
    <div className="overflow-x-auto">
      <div className="flex gap-[3px]">
        {weeks.map((w, i) => (
          <div key={i} className="flex flex-col gap-[3px]">
            {w.map((d, j) =>
              d ? (
                <div
                  key={j}
                  title={`${d.date}: ${formatDuration(d.seconds)}`}
                  className="h-3.5 w-3.5 rounded-[3px]"
                  style={{
                    background: level(d.seconds) ? `rgb(var(--endgames) / ${opacity[level(d.seconds)]})` : "rgb(var(--panel-2))",
                  }}
                />
              ) : (
                <div key={j} className="h-3.5 w-3.5" />
              ),
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
