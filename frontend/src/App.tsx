import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { useAuth } from "./lib/auth";
import Daily from "./pages/Daily";
import Games from "./pages/Games";
import More from "./pages/More";
import Openings from "./pages/Openings";
import Woodpecker from "./pages/Woodpecker";
import Home from "./pages/Home";
import Learn, { OldEndgameRedirect } from "./pages/Learn";
import Login from "./pages/Login";
import Play from "./pages/Play";
import Progress from "./pages/Progress";
import Puzzles from "./pages/Puzzles";
import Review from "./pages/Review";
import Rush from "./pages/Rush";
import Settings from "./pages/Settings";

export default function App() {
  const { user, loading, offline, retry } = useAuth();
  if (loading) return <div className="flex h-screen items-center justify-center text-muted">Cargando…</div>;
  if (offline) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-3 p-4 text-center">
        <p className="font-semibold">No se puede conectar con el servidor.</p>
        <p className="text-sm text-muted">Tu sesión sigue abierta; vuelve a intentarlo en un momento.</p>
        <button className="btn-primary" onClick={retry}>
          Reintentar
        </button>
      </div>
    );
  }
  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<Login />} />
      </Routes>
    );
  }
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="jugar" element={<Play />} />
        <Route path="puzzles" element={<Puzzles />} />
        <Route path="aprender" element={<Learn />} />
        <Route path="aprender/:id" element={<Learn />} />
        <Route path="contrarreloj" element={<Rush />} />
        <Route path="partidas" element={<Games />} />
        <Route path="revision/:id" element={<Review />} />
        <Route path="progreso" element={<Progress />} />
        {/* Los finales viven ahora en Aprender; las direcciones antiguas siguen funcionando */}
        <Route path="finales" element={<Navigate to="/aprender?curso=finales" replace />} />
        <Route path="finales/:id" element={<OldEndgameRedirect />} />
        <Route path="aperturas" element={<Openings />} />
        <Route path="woodpecker" element={<Woodpecker />} />
        <Route path="retos" element={<Daily />} />
        <Route path="mas" element={<More />} />
        <Route path="ajustes" element={<Settings />} />
        <Route path="login" element={<Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
