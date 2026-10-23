import { useEffect, useRef } from "react";
import { Chessground } from "@lichess-org/chessground";
import type { Api } from "@lichess-org/chessground/api";
import type { DrawBrushes, DrawShape } from "@lichess-org/chessground/draw";
import type { Key } from "@lichess-org/chessground/types";
import type { Chess, Square } from "chess.js";
import { prefs } from "../lib/prefs";

export type { DrawShape, Key };
export type Color = "white" | "black";

export interface BoardProps {
  fen: string;
  orientation: Color;
  turnColor?: Color;
  /** Color que puede mover; undefined = nadie (tablero de solo lectura para el usuario) */
  movable?: Color;
  dests?: Map<Key, Key[]>;
  lastMove?: Key[];
  check?: boolean;
  shapes?: DrawShape[];
  onMove?: (from: Key, to: Key) => void;
  className?: string;
}

/** Mismo componente para jugar, puzzles y revisión: chessground (el tablero de Lichess). */
export default function Board({
  fen,
  orientation,
  turnColor,
  movable,
  dests,
  lastMove,
  check,
  shapes,
  onMove,
  className = "",
}: BoardProps) {
  const el = useRef<HTMLDivElement>(null);
  const cg = useRef<Api | null>(null);
  const onMoveRef = useRef(onMove);
  onMoveRef.current = onMove;

  // Estado que el tablero debe mostrar según la app. Tras cada jugada se vuelve a aplicar: si la
  // jugada se ha rechazado (fallo en un puzzle, jugada ilegal, promoción cancelada) la posición
  // no cambia, React no repinta y sin esto la pieza se quedaría donde la soltaste.
  const config = {
    fen,
    orientation,
    turnColor: turnColor ?? ((fen.split(" ")[1] === "b" ? "black" : "white") as Color),
    lastMove: lastMove as Key[] | undefined,
    check: check ?? false,
    movable: { color: movable, dests: movable ? dests : new Map<Key, Key[]>() },
  };
  const configRef = useRef(config);
  configRef.current = config;

  useEffect(() => {
    if (!el.current) return;
    cg.current = Chessground(el.current, {
      animation: { enabled: true, duration: 200 },
      highlight: { lastMove: true, check: true },
      premovable: { enabled: false },
      // Pincel blanco para la jugada que se hizo en la partida (revisión); chessground lo añade a los suyos
      drawable: {
        enabled: true,
        brushes: { white: { key: "w", color: "#ffffff", opacity: 0.8, lineWidth: 10 } } as unknown as DrawBrushes,
      },
      movable: {
        free: false,
        showDests: true,
        events: {
          after: (orig, dest) => {
            onMoveRef.current?.(orig, dest);
            // Después de que React procese la jugada, el tablero vuelve a la posición real
            window.setTimeout(() => cg.current?.set(configRef.current), 0);
          },
        },
      },
    });
    return () => cg.current?.destroy();
  }, []);

  useEffect(() => {
    cg.current?.set(configRef.current);
  }, [fen, orientation, turnColor, movable, dests, lastMove, check]);

  useEffect(() => {
    cg.current?.setAutoShapes(shapes ?? []);
  }, [shapes]);

  return (
    <div className={`board-wrap board-${prefs.board} ${className}`}>
      <div ref={el} />
    </div>
  );
}

export function toDests(chess: Chess): Map<Key, Key[]> {
  const dests = new Map<Key, Key[]>();
  for (const m of chess.moves({ verbose: true })) {
    const list = dests.get(m.from as Key) ?? [];
    list.push(m.to as Key);
    dests.set(m.from as Key, list);
  }
  return dests;
}

export function isPromotion(chess: Chess, from: string, to: string): boolean {
  const piece = chess.get(from as Square);
  return piece?.type === "p" && (to[1] === "8" || to[1] === "1");
}

export function turnColor(chess: Chess): Color {
  return chess.turn() === "w" ? "white" : "black";
}

export function uciToKeys(uci: string): [Key, Key] {
  return [uci.slice(0, 2) as Key, uci.slice(2, 4) as Key];
}
