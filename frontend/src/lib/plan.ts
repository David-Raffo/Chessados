import type { PlanStep } from "./types";

// Actividades de useActivity que cuentan para cada paso por tiempo (igual que backend/app/plan.py)
export const TIMED: Record<string, { area: string; activities: string[] | null }> = {
  puzzles: { area: "tactics", activities: ["puzzles", "review"] },
  woodpecker: { area: "tactics", activities: ["woodpecker"] },
  endgame: { area: "endgames", activities: null },
  openings: { area: "openings", activities: null },
};

export function stepLink(s: PlanStep): string {
  switch (s.kind) {
    case "puzzles": {
      const q = new URLSearchParams();
      if (s.area === "endgames") q.set("area", "endgames");
      if (s.theme && s.theme !== "endgame") q.set("theme", s.theme);
      const qs = q.toString();
      return `/puzzles${qs ? `?${qs}` : ""}`;
    }
    case "game":
      return "/jugar?tc=15%2B10";
    case "review":
      return s.game_id ? `/revision/${s.game_id}` : "/partidas";
    case "rush":
      return "/contrarreloj";
    case "endgame":
      return s.lesson_id ? `/finales/${s.lesson_id}` : "/finales";
    case "openings":
      return "/aperturas?tab=train";
    case "woodpecker":
      return "/woodpecker";
    case "daily":
      return "/retos";
  }
}

// --- Paso en curso de «Entrenar hoy» (por navegador y día) -----------------

const KEY = "plan-active";
const today = () => new Date().toDateString();
const listeners = new Set<() => void>();

export function getActiveStep(): number | null {
  try {
    const data = JSON.parse(localStorage.getItem(KEY) ?? "null");
    return data && data.day === today() ? data.index : null;
  } catch {
    return null;
  }
}

export function setActiveStep(index: number | null) {
  try {
    if (index == null) localStorage.removeItem(KEY);
    else localStorage.setItem(KEY, JSON.stringify({ day: today(), index }));
  } catch {
    /* almacenamiento no disponible */
  }
  listeners.forEach((l) => l());
}

export function onActiveStepChange(fn: () => void) {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}
