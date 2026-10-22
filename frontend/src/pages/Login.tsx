import { useEffect, useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

const LEVELS = [
  { value: 800, label: "Empiezo", hint: "Conozco las reglas" },
  { value: 1200, label: "Intermedio", hint: "Juego a menudo" },
  { value: 1600, label: "Avanzado", hint: "Club o +1600 online" },
];

// Enlace de invitación: https://…/?invitacion=ABCD-EFGH abre el registro con el código puesto
const linkCode = new URLSearchParams(window.location.search).get("invitacion") ?? "";

export default function Login() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">(linkCode ? "register" : "login");
  const [inviteCode, setInviteCode] = useState(linkCode);
  const [firstAccount, setFirstAccount] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [level, setLevel] = useState(1200);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<{ first_account: boolean }>("/auth/setup")
      .then((r) => setFirstAccount(r.first_account))
      .catch(() => undefined);
  }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(username, password);
      else await register({ username, password, level, invite_code: firstAccount ? null : inviteCode });
      if (linkCode) window.history.replaceState(null, "", "/");
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
        {mode === "register" &&
          (firstAccount ? (
            <p className="rounded-xl bg-panel2 p-3 text-sm">
              Es la primera cuenta de esta instalación: no necesita invitación y será la de administrador, con
              invitaciones ilimitadas.
            </p>
          ) : (
            <div>
              <label className="label">Código de invitación</label>
              <input
                className="input font-mono uppercase tracking-wider"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
                placeholder="ABCD-EFGH"
                autoCapitalize="characters"
                autoComplete="off"
                required
              />
              <p className="mt-1 text-xs text-muted">Pídeselo a alguien que ya tenga cuenta.</p>
            </div>
          ))}
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
