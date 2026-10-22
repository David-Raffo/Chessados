// Preferencias de este navegador (no hace falta que viajen al servidor)

function read(key: string, fallback: string): string {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}

function write(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* almacenamiento no disponible */
  }
}

export type BoardTheme = "brown" | "blue" | "green";

export const prefs = {
  get dark() {
    return read("theme", "dark") !== "light";
  },
  set dark(v: boolean) {
    write("theme", v ? "dark" : "light");
    document.documentElement.classList.toggle("dark", v);
  },
  get board(): BoardTheme {
    return read("board", "brown") as BoardTheme;
  },
  set board(v: BoardTheme) {
    write("board", v);
  },
  get sound() {
    return read("sound", "on") === "on";
  },
  set sound(v: boolean) {
    write("sound", v ? "on" : "off");
  },
  /** Mostrar el objetivo del puzzle («Mate en 2», «Gana material»…) antes de resolverlo */
  get puzzleGoal() {
    return read("puzzle-goal", "off") === "on";
  },
  set puzzleGoal(v: boolean) {
    write("puzzle-goal", v ? "on" : "off");
  },
};
