import type { Area, RatingArea } from "./types";

export const AREA_LABEL: Record<Area | RatingArea, string> = {
  tactics: "Táctica",
  play: "Partidas",
  endgames: "Finales",
  openings: "Aperturas",
  rush: "Contrarreloj",
};

export const AREA_TEXT: Record<string, string> = {
  tactics: "text-tactics",
  play: "text-play",
  endgames: "text-endgames",
  openings: "text-openings",
  rush: "text-rush",
};

export const AREA_BG: Record<string, string> = {
  tactics: "bg-tactics",
  play: "bg-play",
  endgames: "bg-endgames",
  openings: "bg-openings",
  rush: "bg-rush",
};

export const AREA_COLOR_VAR: Record<string, string> = {
  tactics: "rgb(var(--tactics))",
  play: "rgb(var(--play))",
  endgames: "rgb(var(--endgames))",
  openings: "rgb(var(--openings))",
  rush: "rgb(var(--rush))",
};

/** Temas de la base de puzzles de Lichess con su nombre en español. */
export const THEMES: Record<string, string> = {
  fork: "Horquilla",
  pin: "Clavada",
  skewer: "Enfilada",
  discoveredAttack: "Ataque a la descubierta",
  doubleCheck: "Jaque doble",
  hangingPiece: "Pieza colgada",
  trappedPiece: "Pieza atrapada",
  sacrifice: "Sacrificio",
  deflection: "Desviación",
  attraction: "Atracción",
  clearance: "Despeje",
  interference: "Interferencia",
  intermezzo: "Jugada intermedia",
  quietMove: "Jugada tranquila",
  xRayAttack: "Rayos X",
  zugzwang: "Zugzwang",
  capturingDefender: "Eliminar al defensor",
  exposedKing: "Rey expuesto",
  kingsideAttack: "Ataque en el flanco de rey",
  queensideAttack: "Ataque en el flanco de dama",
  advancedPawn: "Peón avanzado",
  promotion: "Promoción",
  underPromotion: "Subpromoción",
  defensiveMove: "Jugada defensiva",
  mate: "Mate",
  mateIn1: "Mate en 1",
  mateIn2: "Mate en 2",
  mateIn3: "Mate en 3",
  mateIn4: "Mate en 4",
  mateIn5: "Mate en 5 o más",
  backRankMate: "Mate del pasillo",
  smotheredMate: "Mate de la coz",
  anastasiaMate: "Mate de Anastasia",
  arabianMate: "Mate árabe",
  bodenMate: "Mate de Boden",
  hookMate: "Mate del gancho",
  dovetailMate: "Mate de la cola de milano",
  opening: "Apertura",
  middlegame: "Medio juego",
  endgame: "Final",
  rookEndgame: "Final de torres",
  bishopEndgame: "Final de alfiles",
  knightEndgame: "Final de caballos",
  pawnEndgame: "Final de peones",
  queenEndgame: "Final de damas",
  queenRookEndgame: "Final de dama y torre",
  castling: "Enroque",
  enPassant: "Captura al paso",
  short: "Corto",
  long: "Largo",
  veryLong: "Muy largo",
  oneMove: "Una jugada",
  crushing: "Aplastante",
  advantage: "Ventaja",
  equality: "Igualdad",
  master: "Partida de maestros",
  masterVsMaster: "Maestro contra maestro",
  superGM: "Súper GM",
  attackingF2F7: "Ataque a f2/f7",
};

export const THEME_FILTERS = [
  "fork", "pin", "skewer", "discoveredAttack", "hangingPiece", "sacrifice", "deflection", "attraction",
  "mateIn1", "mateIn2", "mateIn3", "backRankMate", "endgame", "rookEndgame", "pawnEndgame", "promotion",
  "trappedPiece", "intermezzo", "quietMove", "zugzwang",
];

/** Objetivo del puzzle a partir de sus temas de Lichess (es una pista, por eso es opcional). */
export function puzzleGoal(themes: string[]): string {
  const mate = themes.find((t) => /^mateIn\d$/.test(t));
  if (mate) {
    const n = Number(mate.slice(6));
    return n >= 5 ? "Da mate en 5 o más" : `Mate en ${n}`;
  }
  if (themes.includes("mate")) return "Da mate";
  if (themes.includes("equality")) return "Salva la posición";
  if (themes.includes("crushing")) return "Consigue una ventaja decisiva";
  if (themes.includes("advantage")) return "Consigue ventaja";
  return "Encuentra la mejor jugada";
}

export const themeLabel = (t: string) => THEMES[t] ?? t;

export const CLASS_LABEL: Record<string, string> = {
  best: "Mejor jugada",
  good: "Buena",
  inaccuracy: "Imprecisión",
  mistake: "Error",
  blunder: "Error grave",
};

export const CLASS_SYMBOL: Record<string, string> = {
  best: "",
  good: "",
  inaccuracy: "?!",
  mistake: "?",
  blunder: "??",
};

export const CLASS_TEXT: Record<string, string> = {
  best: "text-good",
  good: "text-fg",
  inaccuracy: "text-tactics",
  mistake: "text-rush",
  blunder: "text-bad",
};

export const PHASE_LABEL: Record<string, string> = {
  opening: "Apertura",
  middlegame: "Medio juego",
  endgame: "Final",
};

export function opponentName(g: { opponent: string; opponent_elo: number | null }): string {
  if (g.opponent === "stockfish") return `Stockfish ${g.opponent_elo ?? ""}`.trim();
  if (g.opponent === "maia") return `Maia ${g.opponent_elo ?? ""}`.trim();
  return g.opponent;
}

export function formatDuration(seconds: number): string {
  const m = Math.round(seconds / 60);
  if (m < 60) return `${m} min`;
  const h = Math.floor(m / 60);
  const r = m % 60;
  return r ? `${h} h ${String(r).padStart(2, "0")} min` : `${h} h`;
}

export function formatClock(ms: number): string {
  if (ms > 0 && ms < 10_000) return `0:0${Math.floor(ms / 1000)}.${Math.floor((ms % 1000) / 100)}`;
  const total = Math.max(0, Math.ceil(ms / 1000));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}
