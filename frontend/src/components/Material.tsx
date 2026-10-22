import type { Color } from "./Board";

const START: Record<string, number> = { p: 8, n: 2, b: 2, r: 2, q: 1 };
const VALUE: Record<string, number> = { p: 1, n: 3, b: 3, r: 5, q: 9 };
const ORDER = ["p", "n", "b", "r", "q"];
const ROLE: Record<string, string> = { p: "pawn", n: "knight", b: "bishop", r: "rook", q: "queen" };

export interface MaterialInfo {
  /** Piezas que ha capturado cada bando (es decir, las que le faltan al rival). */
  captured: Record<Color, string[]>;
  /** Ventaja de material de las blancas (negativa si van por delante las negras). */
  diff: number;
}

/** Cuenta el material de una posición FEN. Con promociones, las piezas de más no cuentan como capturadas. */
export function material(fen: string): MaterialInfo {
  const counts: Record<Color, Record<string, number>> = {
    white: { p: 0, n: 0, b: 0, r: 0, q: 0 },
    black: { p: 0, n: 0, b: 0, r: 0, q: 0 },
  };
  for (const ch of fen.split(" ")[0]) {
    const t = ch.toLowerCase();
    if (!(t in START)) continue;
    counts[ch === t ? "black" : "white"][t] += 1;
  }
  const missing = (c: Color) => {
    // Cada pieza de más que el inicial salió de un peón coronado: ese peón no fue capturado
    const promoted = ORDER.slice(1).reduce((s, t) => s + Math.max(0, counts[c][t] - START[t]), 0);
    return ORDER.flatMap((t) => {
      const gone = START[t] - counts[c][t] - (t === "p" ? promoted : 0);
      return Array(Math.max(0, gone)).fill(t);
    });
  };
  const score = (c: Color) => ORDER.reduce((s, t) => s + counts[c][t] * VALUE[t], 0);
  return {
    captured: { white: missing("black"), black: missing("white") },
    diff: score("white") - score("black"),
  };
}

/** Fila de piezas capturadas por `side` y su ventaja («+3») si va por delante. */
export function Captured({ info, side }: { info: MaterialInfo; side: Color }) {
  const pieces = info.captured[side];
  const lead = side === "white" ? info.diff : -info.diff;
  const opponent: Color = side === "white" ? "black" : "white";
  if (!pieces.length && lead <= 0) return null;
  return (
    // Mismas piezas que el tablero (cburnett): la clase .cg-wrap activa sus imágenes
    <span className="cg-wrap captured flex items-center gap-1.5" aria-label="Piezas capturadas">
      {pieces.length > 0 && (
        // Fondo claro: las piezas negras no se ven sobre el tema oscuro
        <span className="flex items-center rounded-md bg-neutral-200/90 px-1 py-0.5">
          {pieces.map((t, i) => (
            // Piezas iguales se solapan, como en Lichess
            <piece key={i} className={`${ROLE[t]} ${opponent} ${i > 0 && pieces[i - 1] === t ? "-ml-3" : ""}`} />
          ))}
        </span>
      )}
      {lead > 0 && <span className="text-base font-bold text-fg">+{lead}</span>}
    </span>
  );
}
