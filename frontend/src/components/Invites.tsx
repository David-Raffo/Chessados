import { useEffect, useState } from "react";
import { api } from "../lib/api";

interface InviteList {
  limit: number | null; // null = ilimitadas (administrador)
  created: number;
  codes: { code: string; created_at: string; used: boolean; used_by: string | null; used_at: string | null }[];
}

const linkFor = (code: string) => `${window.location.origin}/?invitacion=${code}`;

/** Invitaciones de la cuenta: crear, copiar el enlace y anular las que no se han usado. */
export default function Invites() {
  const [data, setData] = useState<InviteList | null>(null);
  const [msg, setMsg] = useState("");
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    api<InviteList>("/invites").then(setData).catch(() => undefined);
  }, []);

  async function create() {
    setMsg("");
    try {
      setData(await api<InviteList>("/invites", { method: "POST" }));
    } catch (e) {
      setMsg((e as Error).message);
    }
  }

  async function revoke(code: string) {
    if (!window.confirm(`¿Anular la invitación ${code}?`)) return;
    setData(await api<InviteList>(`/invites/${code}`, { method: "DELETE" }));
  }

  async function copy(code: string) {
    try {
      await navigator.clipboard.writeText(linkFor(code));
      setCopied(code);
      window.setTimeout(() => setCopied(null), 1500);
    } catch {
      window.prompt("Copia el enlace de invitación:", linkFor(code));
    }
  }

  if (!data) return null;
  const left = data.limit === null ? null : data.limit - data.created;

  return (
    <section className="card space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-bold">Invitaciones</h2>
        <span className="text-sm text-muted">
          {left === null ? "Ilimitadas (administrador)" : `Te quedan ${left} de ${data.limit}`}
        </span>
      </div>
      <p className="text-sm text-muted">
        Para crear una cuenta hace falta un código. Cada código sirve una vez; anular uno sin usar te devuelve el hueco.
      </p>
      <button className="btn-primary" onClick={create} disabled={left !== null && left <= 0}>
        Crear invitación
      </button>
      {msg && <p className="text-sm text-bad">{msg}</p>}
      {data.codes.length > 0 && (
        <ul className="divide-y divide-line rounded-xl border border-line">
          {data.codes.map((c) => (
            <li key={c.code} className="flex flex-wrap items-center gap-3 px-3 py-2 text-sm">
              <span className={`font-mono font-bold tracking-wider ${c.used ? "text-muted line-through" : ""}`}>{c.code}</span>
              <span className="flex-1 text-muted">
                {c.used ? `Usada por ${c.used_by ?? "una cuenta borrada"}` : "Sin usar"}
              </span>
              {!c.used && (
                <>
                  <button className="btn-ghost px-3 py-1" onClick={() => copy(c.code)}>
                    {copied === c.code ? "¡Copiado!" : "Copiar enlace"}
                  </button>
                  <button className="text-bad hover:underline" onClick={() => revoke(c.code)}>
                    Anular
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
