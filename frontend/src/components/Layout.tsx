import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../lib/auth";
import PlanBanner from "./PlanBanner";

export const MODULES = [
  { to: "/", label: "Inicio", icon: "M3 11l9-8 9 8v10a1 1 0 01-1 1h-5v-7H9v7H4a1 1 0 01-1-1z" },
  { to: "/jugar", label: "Jugar", icon: "M9 3h6l-1 4h3l-2 5h-8L5 7h3zM6 14h12l1 4H5zM4 20h16v2H4z" },
  { to: "/puzzles", label: "Puzzles", icon: "M10 3a2 2 0 014 0v2h4a1 1 0 011 1v4h-2a2 2 0 000 4h2v4a1 1 0 01-1 1h-4v-2a2 2 0 00-4 0v2H6a1 1 0 01-1-1v-4h2a2 2 0 000-4H5V6a1 1 0 011-1h4z" },
  { to: "/contrarreloj", label: "Contrarreloj", icon: "M12 22a9 9 0 110-18 9 9 0 010 18zm0-2a7 7 0 100-14 7 7 0 000 14zm1-11v4.6l3 1.8-1 1.6-4-2.4V9zM9 1h6v2H9z" },
  { to: "/finales", label: "Finales", icon: "M7 21h10v-2H7zm1-4h8l-1-6h2V9h-3.2A3 3 0 0012 4a3 3 0 00-1.8 5H7v2h2z" },
  { to: "/aperturas", label: "Aperturas", icon: "M4 5a2 2 0 012-2h5v18H6a2 2 0 01-2-2zm9-2h5a2 2 0 012 2v14a2 2 0 01-2 2h-5z" },
  { to: "/woodpecker", label: "Woodpecker", icon: "M4 12a8 8 0 0114-5.3V4h2v7h-7V9h3.5A6 6 0 106 12z" },
  { to: "/retos", label: "Desafíos", icon: "M12 2l3 6.5 7 .8-5.2 4.8 1.4 7L12 17.6 5.8 21l1.4-7L2 9.3l7-.8z" },
  { to: "/partidas", label: "Partidas", icon: "M4 4h16v4H4zM4 10h16v4H4zM4 16h10v4H4z" },
  { to: "/progreso", label: "Progreso", icon: "M4 20V10h3v10zm6.5 0V4h3v16zM17 20v-7h3v7z" },
];

function Icon({ d }: { d: string }) {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current" aria-hidden>
      <path d={d} />
    </svg>
  );
}

export default function Layout() {
  const { user, logout } = useAuth();
  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-56 shrink-0 flex-col border-r border-line bg-panel p-4 md:flex">
        <div className="mb-8 flex items-center gap-2 px-2 text-lg font-extrabold">
          <img src="/icon.svg" alt="" className="h-8 w-8" />
          Chessados
        </div>
        <nav className="flex flex-col gap-1">
          {MODULES.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2 font-medium transition ${
                  isActive ? "bg-panel2 text-fg" : "text-muted hover:bg-panel2 hover:text-fg"
                }`
              }
            >
              <Icon d={l.icon} />
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto flex flex-col gap-1 text-sm">
          <NavLink to="/ajustes" className="rounded-xl px-3 py-2 text-muted hover:bg-panel2 hover:text-fg">
            ⚙ Ajustes · {user?.name}
          </NavLink>
          <button className="rounded-xl px-3 py-2 text-left text-muted hover:bg-panel2 hover:text-fg" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 px-4 pb-24 pt-4 md:px-8 md:pb-8 md:pt-8">
        <PlanBanner />
        <div className="mx-auto max-w-6xl">
          <Outlet />
        </div>
      </main>

      {/* Navegación inferior en móvil */}
      <nav className="fixed inset-x-0 bottom-0 z-30 flex justify-around border-t border-line bg-panel/95 pb-[env(safe-area-inset-bottom)] backdrop-blur md:hidden">
        {[
          MODULES[0],
          MODULES[1],
          MODULES[2],
          MODULES.find((m) => m.to === "/progreso")!,
          { to: "/mas", label: "Más", icon: "M5 10a2 2 0 110 4 2 2 0 010-4zm7 0a2 2 0 110 4 2 2 0 010-4zm7 0a2 2 0 110 4 2 2 0 010-4z" },
        ].map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px] ${isActive ? "text-fg" : "text-muted"}`
            }
          >
            <Icon d={l.icon} />
            {l.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
