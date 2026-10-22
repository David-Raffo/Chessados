// Partida en curso guardada en el navegador: si recargas o sales a mitad, se puede continuar
// (o abandonar, que cuenta como derrota). Así salir no sirve para librarse de perder.

export interface OngoingGame {
  color: "white" | "black";
  elo: number;
  // Configuración de la partida (rival, ritmo, escalera…); se guarda tal cual
  setup: {
    rival: "stockfish" | "maia";
    maiaLevel: number;
    ladder: boolean;
    elo: number;
    color: "white" | "black" | "random";
    tc: { id: string; minutes: number; inc: number; label: string; hint: string };
  };
  moves: string[]; // UCI
  clocks: { white: number; black: number };
  savedAt: number;
}

const KEY = "play-ongoing";

export function loadOngoing(): OngoingGame | null {
  try {
    const data = JSON.parse(localStorage.getItem(KEY) ?? "null");
    return data && Array.isArray(data.moves) ? data : null;
  } catch {
    return null;
  }
}

export function saveOngoing(game: OngoingGame) {
  try {
    localStorage.setItem(KEY, JSON.stringify(game));
  } catch {
    /* almacenamiento no disponible */
  }
}

export function clearOngoing() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* almacenamiento no disponible */
  }
}
