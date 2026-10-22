import { useState, type FormEvent } from "react";
import { useAuth } from "../lib/auth";

const LEVELS = [
  { value: 800, label: "Empiezo", hint: "Conozco las reglas" },
  { value: 1200, label: "Intermedio", hint: "Juego a menudo" },
  { value: 1600, label: "Avanzado", hint: "Club o +1600 online" },
];

export default function Login() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [level, setLevel] = useState(1200);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(username, password);
      else await register({ username, password, level });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={submit} className="card w-full max-w-sm animate-pop space-y-4 p-6">
        <div className="flex items-center gap-3">
          <img src="/icon.svg" alt="" className="h-10 w-10" />
          <div>
            <h1 className="text-xl font-extrabold">Chessados</h1>
            <p className="text-sm text-muted">Tu entrenador personal de ajedrez</p>
          </div>
        </div>

        <div className="grid grid-cols-2 rounded-xl bg-panel2 p-1 text-sm font-semibold">
          {(["login", "register"] as const).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={`rounded-lg py-1.5 ${mode === m ? "bg-panel shadow-sm" : "text-muted"}`}
            >
              {m === "login" ? "Entrar" : "Crear cuenta"}
            </button>
          ))}
        </div>

        <div>
          <label className="label">Usuario</label>
          <input
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            autoCapitalize="none"
            minLength={3}
            maxLength={30}
            required
          />
        </div>
        <div>
          <label className="label">Contraseña</label>
          <input
            className="input"
            type="password"
            minLength={4}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {mode === "register" && (
          <div>
            <label className="label">¿Qué nivel tienes?</label>
            <div className="grid grid-cols-3 gap-2">
              {LEVELS.map((l) => (
                <button
                  type="button"
                  key={l.value}
                  onClick={() => setLevel(l.value)}
                  className={`rounded-xl border p-2 text-left text-sm ${
                    level === l.value ? "border-fg bg-panel2" : "border-line"
                  }`}
                >
                  <div className="font-semibold">{l.label}</div>
                  <div className="text-xs text-muted">{l.hint}</div>
                </button>
              ))}
            </div>
          </div>
        )}
        {error && <p className="text-sm text-bad">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>
          {mode === "login" ? "Entrar" : "Empezar a entrenar"}
        </button>
      </form>
    </div>
  );
}
