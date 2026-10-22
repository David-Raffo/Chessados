import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { useAuth } from "./lib/auth";
import Daily from "./pages/Daily";
import Endgames from "./pages/Endgames";
import Games from "./pages/Games";
import More from "./pages/More";
import Openings from "./pages/Openings";
import Woodpecker from "./pages/Woodpecker";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Play from "./pages/Play";
import Progress from "./pages/Progress";
import Puzzles from "./pages/Puzzles";
import Review from "./pages/Review";
import Rush from "./pages/Rush";
import Settings from "./pages/Settings";

export default function App() {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex h-screen items-center justify-center text-muted">Cargando…</div>;
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
        <Route path="contrarreloj" element={<Rush />} />
        <Route path="partidas" element={<Games />} />
        <Route path="revision/:id" element={<Review />} />
        <Route path="progreso" element={<Progress />} />
        <Route path="finales" element={<Endgames />} />
        <Route path="finales/:id" element={<Endgames />} />
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
