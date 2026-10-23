import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { opponentName } from "../lib/labels";
import type { Game } from "../lib/types";

const RESULT_STYLE: Record<string, string> = { win: "bg-good", loss: "bg-bad", draw: "bg-muted" };
const RESULT_TEXT: Record<string, string> = { win: "Victoria", loss: "Derrota", draw: "Tablas" };
const SOURCE: Record<string, string> = { app: "Chessados", pgn: "PGN", lichess: "Lichess", chesscom: "Chess.com" };

export default function Games() {
  const { user } = useAuth();
  const [games, setGames] = useState<Game[] | null>(null);
  const [tab, setTab] = useState<"lichess" | "chesscom" | "pgn">("lichess");
  const [username, setUsername] = useState(user?.lichess_username ?? "");
  const [pgn, setPgn] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = useCallback(() => {
    api<Game[]>("/games").then(setGames).catch(() => setGames([]));
  }, []);
  useEffect(load, [load]);

  // Refresca mientras haya partidas en la cola de análisis
  useEffect(() => {
    if (!games?.some((g) => ["pending", "running", "quick", "refining"].includes(g.analysis_status))) return;
    const t = window.setTimeout(load, 5000);
    return () => window.clearTimeout(t);
  }, [games, load]);

  useEffect(() => {
    setUsername((tab === "chesscom" ? user?.chesscom_username : user?.lichess_username) ?? "");
  }, [tab, user]);

  async function doImport() {
    setBusy(true);
    setMsg("");
    try {
      const r = await api<{ imported: number; skipped: number }>(
        `/games/import/${tab}`,
        { body: tab === "pgn" ? { pgn, username: username || null } : { username, max: 20 } },
      );
      setMsg(`${r.imported} partidas importadas${r.skipped ? `, ${r.skipped} omitidas` : ""}. Se analizarán en segundo plano.`);
      setPgn("");
      load();
    } catch (e) {
      setMsg((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-extrabold">Partidas</h1>
        <p className="text-muted">Cada partida se analiza con Stockfish. Revísala tú primero y después mira el motor.</p>
      </header>

      <section className="card space-y-3">
        <div className="flex flex-wrap gap-2">
          {(
            [
              ["lichess", "Importar de Lichess"],
              ["chesscom", "Importar de Chess.com"],
              ["pgn", "Pegar PGN"],
            ] as const
          ).map(([t, label]) => (
            <button key={t} className={`chip ${tab === t ? "chip-on" : ""}`} onClick={() => setTab(t)}>
              {label}
            </button>
          ))}
        </div>
        {tab === "pgn" ? (
          <>
            <textarea
              className="input min-h-28 font-mono text-xs"
              placeholder='[Event "..."]&#10;1. e4 e5 2. Cf3 ...'
              value={pgn}
              onChange={(e) => setPgn(e.target.value)}
            />
            <input
              className="input"
              placeholder="Tu nombre en el PGN (para saber qué color llevabas)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </>
        ) : (
          <input
            className="input"
            placeholder={tab === "lichess" ? "Usuario de Lichess" : "Usuario de Chess.com"}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        )}
        <div className="flex items-center gap-3">
          <button
            className="btn-primary"
            disabled={busy || (tab === "pgn" ? !pgn.trim() : username.trim().length < 2)}
            onClick={doImport}
          >
            {busy ? "Importando…" : tab === "pgn" ? "Importar" : "Importar últimas 20"}
          </button>
          {msg && <span className="text-sm text-muted">{msg}</span>}
        </div>
      </section>

      <section className="card p-0">
        {games === null && <p className="p-4 text-muted">Cargando…</p>}
        {games?.length === 0 && (
          <p className="p-4 text-muted">
            Aún no hay partidas. <Link to="/jugar" className="underline">Juega una contra Stockfish</Link> o importa las tuyas.
          </p>
        )}
        <ul className="divide-y divide-line">
          {games?.map((g) => (
            <li key={g.id}>
              <Link to={`/revision/${g.id}`} className="flex items-center gap-3 px-4 py-3 hover:bg-panel2">
                <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${RESULT_STYLE[g.user_result ?? ""] ?? "bg-line"}`} />
                <div className="min-w-0 flex-1">
                  <div className="line-clamp-2 font-semibold leading-snug">
                    {RESULT_TEXT[g.user_result ?? ""] ?? g.result} contra {opponentName(g)}
                    {g.opponent_elo && !["stockfish", "maia"].includes(g.opponent) ? ` (${g.opponent_elo})` : ""}
                  </div>
                  <div className="text-xs text-muted">
                    {g.played_at ? new Date(g.played_at).toLocaleDateString("es-ES", { day: "numeric", month: "short", year: "numeric" }) : ""}
                    {" · "}
                    {g.user_color === "white" ? "Blancas" : "Negras"} · {SOURCE[g.source] ?? g.source}
                    {g.time_control ? ` · ${g.time_control}` : ""}
                  </div>
                </div>
                <div className="text-right text-xs">
                  {["quick", "refining", "done"].includes(g.analysis_status) ? (
                    g.accuracy != null && <div className="font-bold">{g.accuracy}%</div>
                  ) : g.analysis_status === "error" ? (
                    <div className="text-bad">Error</div>
                  ) : (
                    <div className="animate-pulse text-muted">Analizando…</div>
                  )}
                  {g.reviewed ? (
                    <div className="text-good">Revisada</div>
                  ) : (
                    <div className="text-tactics">Por revisar</div>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
