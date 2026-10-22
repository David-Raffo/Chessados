import { useState } from "react";
import Invites from "../components/Invites";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { AREA_LABEL, AREA_TEXT, formatDuration } from "../lib/labels";
import { prefs, type BoardTheme } from "../lib/prefs";
import type { Area, User } from "../lib/types";

const AREAS: Area[] = ["tactics", "play", "endgames", "openings"];

export default function Settings() {
  const { user, setUser, logout } = useAuth();
  const [form, setForm] = useState(() => ({
    name: user!.name,
    weekly_hours: user!.weekly_hours,
    target_split: { ...user!.target_split },
    review_lock: user!.review_lock,
    ladder_elo: user!.ladder_elo,
    lichess_username: user!.lichess_username ?? "",
    chesscom_username: user!.chesscom_username ?? "",
  }));
  const [dark, setDark] = useState(prefs.dark);
  const [board, setBoard] = useState<BoardTheme>(prefs.board);
  const [soundOn, setSoundOn] = useState(prefs.sound);
  const [msg, setMsg] = useState("");

  const total = AREAS.reduce((a, k) => a + Number(form.target_split[k] || 0), 0);

  async function save() {
    setMsg("");
    try {
      const u = await api<User>("/me", { method: "PATCH", body: form });
      setUser(u);
      setMsg("Guardado ✓");
    } catch (e) {
      setMsg((e as Error).message);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-extrabold">Perfil y ajustes</h1>

      <section className="card space-y-4">
        <h2 className="font-bold">Objetivos</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Nombre</label>
            <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div>
            <label className="label">Horas por semana</label>
            <input
              className="input"
              type="number"
              min={1}
              max={60}
              step={0.5}
              value={form.weekly_hours}
              onChange={(e) => setForm({ ...form, weekly_hours: Number(e.target.value) })}
            />
          </div>
        </div>
        <div>
          <label className="label">
            Reparto objetivo{" "}
            <span className={Math.abs(total - 100) > 0.5 ? "text-bad" : "text-good"}>({total}% de 100%)</span>
          </label>
          <div className="space-y-3">
            {AREAS.map((a) => (
              <div key={a} className="grid grid-cols-[7rem_1fr_3.5rem_5.5rem] items-center gap-3 text-sm">
                <span className={`font-semibold ${AREA_TEXT[a]}`}>{AREA_LABEL[a]}</span>
                <input
                  type="range"
                  min={0}
                  max={80}
                  step={5}
                  value={form.target_split[a]}
                  onChange={(e) => setForm({ ...form, target_split: { ...form.target_split, [a]: Number(e.target.value) } })}
                />
                <span className="text-right font-bold">{form.target_split[a]}%</span>
                <span className="text-muted">{formatDuration((form.weekly_hours * 3600 * form.target_split[a]) / 100)}</span>
              </div>
            ))}
          </div>
          <p className="mt-2 text-xs text-muted">
            Por defecto: táctica 40%, partidas 35%, finales 15%, aperturas 10% (Kuljasevic y Studer).
          </p>
        </div>
        <label className="flex items-center justify-between gap-4">
          <span>
            <span className="font-medium">Bloquear partidas sin revisar</span>
            <span className="block text-sm text-muted">No podrás jugar otra hasta revisar la anterior.</span>
          </span>
          <input
            type="checkbox"
            className="h-5 w-5"
            checked={form.review_lock}
            onChange={(e) => setForm({ ...form, review_lock: e.target.checked })}
          />
        </label>
        <div>
          <label className="label">ELO actual de la escalera</label>
          <input
            className="input"
            type="number"
            min={400}
            max={3000}
            step={50}
            value={form.ladder_elo}
            onChange={(e) => setForm({ ...form, ladder_elo: Number(e.target.value) })}
          />
        </div>
      </section>

      <section className="card space-y-4">
        <h2 className="font-bold">Cuentas para importar partidas</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Usuario de Lichess</label>
            <input
              className="input"
              value={form.lichess_username}
              onChange={(e) => setForm({ ...form, lichess_username: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Usuario de Chess.com</label>
            <input
              className="input"
              value={form.chesscom_username}
              onChange={(e) => setForm({ ...form, chesscom_username: e.target.value })}
            />
          </div>
        </div>
      </section>

      <div className="flex items-center gap-3">
        <button className="btn-primary" onClick={save} disabled={Math.abs(total - 100) > 0.5}>
          Guardar cambios
        </button>
        {msg && <span className="text-sm text-muted">{msg}</span>}
      </div>

      <Invites />

      <section className="card space-y-4">
        <h2 className="font-bold">Este dispositivo</h2>
        <label className="flex items-center justify-between">
          <span className="font-medium">Tema oscuro</span>
          <input
            type="checkbox"
            className="h-5 w-5"
            checked={dark}
            onChange={(e) => {
              prefs.dark = e.target.checked;
              setDark(e.target.checked);
            }}
          />
        </label>
        <label className="flex items-center justify-between">
          <span className="font-medium">Sonidos</span>
          <input
            type="checkbox"
            className="h-5 w-5"
            checked={soundOn}
            onChange={(e) => {
              prefs.sound = e.target.checked;
              setSoundOn(e.target.checked);
            }}
          />
        </label>
        <div>
          <span className="label">Tablero</span>
          <div className="flex gap-2">
            {(
              [
                ["brown", "Madera", "#b58863", "#f0d9b5"],
                ["blue", "Azul", "#8ca2ad", "#dee3e6"],
                ["green", "Verde", "#86a666", "#ffffdd"],
              ] as const
            ).map(([id, label, dark, light]) => (
              <button
                key={id}
                onClick={() => {
                  prefs.board = id;
                  setBoard(id);
                }}
                className={`flex items-center gap-2 rounded-xl border p-2 pr-3 ${board === id ? "border-fg" : "border-line"}`}
              >
                <span className="grid h-8 w-8 grid-cols-2 overflow-hidden rounded">
                  <span style={{ background: light }} />
                  <span style={{ background: dark }} />
                  <span style={{ background: dark }} />
                  <span style={{ background: light }} />
                </span>
                {label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <button className="btn-ghost text-bad" onClick={logout}>
        Cerrar sesión
      </button>
    </div>
  );
}
