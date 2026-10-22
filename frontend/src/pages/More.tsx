import { Link } from "react-router-dom";
import { MODULES } from "../components/Layout";

/** Todos los módulos, para la navegación en móvil. */
export default function More() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-extrabold">Módulos</h1>
      <div className="grid grid-cols-2 gap-3">
        {MODULES.map((m) => (
          <Link key={m.to} to={m.to} className="card flex flex-col gap-2 transition hover:bg-panel2">
            <svg viewBox="0 0 24 24" className="h-6 w-6 fill-current" aria-hidden>
              <path d={m.icon} />
            </svg>
            <span className="font-semibold">{m.label}</span>
          </Link>
        ))}
        <Link to="/ajustes" className="card transition hover:bg-panel2">
          <span className="font-semibold">⚙ Ajustes</span>
        </Link>
      </div>
    </div>
  );
}
