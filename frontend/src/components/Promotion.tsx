import type { Color } from "./Board";

const PIECES: { role: "q" | "r" | "b" | "n"; white: string; black: string; label: string }[] = [
  { role: "q", white: "♕", black: "♛", label: "Dama" },
  { role: "r", white: "♖", black: "♜", label: "Torre" },
  { role: "b", white: "♗", black: "♝", label: "Alfil" },
  { role: "n", white: "♘", black: "♞", label: "Caballo" },
];

export default function Promotion({
  color,
  onPick,
  onCancel,
}: {
  color: Color;
  onPick: (role: "q" | "r" | "b" | "n") => void;
  onCancel: () => void;
}) {
  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/50" onClick={onCancel}>
      <div className="card flex animate-pop gap-2" onClick={(e) => e.stopPropagation()}>
        {PIECES.map((p) => (
          <button
            key={p.role}
            title={p.label}
            className="h-16 w-16 rounded-xl bg-panel2 text-5xl leading-none hover:bg-line"
            onClick={() => onPick(p.role)}
          >
            {color === "white" ? p.white : p.black}
          </button>
        ))}
      </div>
    </div>
  );
}
