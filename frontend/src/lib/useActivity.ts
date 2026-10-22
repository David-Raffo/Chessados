import { useEffect, useRef } from "react";
import { api } from "./api";
import type { Area } from "./types";

const IDLE_MS = 2 * 60 * 1000; // tras 2 minutos sin interacción el contador se pausa
const BEAT_MS = 30 * 1000;

/**
 * Registra el tiempo activo en un área mientras el componente está montado.
 * Solo cuenta segundos con interacción reciente (clic, tecla, toque).
 */
export function useActivity(area: Area | null, activity: string, refId?: string | number) {
  const lastInteraction = useRef(Date.now());

  useEffect(() => {
    if (!area) return;
    let sessionId: number | null = null;
    let active = 0;
    let sent = 0;
    let stopped = false;
    lastInteraction.current = Date.now();

    const touch = () => (lastInteraction.current = Date.now());
    const events = ["pointerdown", "keydown", "wheel", "touchstart"] as const;
    events.forEach((e) => window.addEventListener(e, touch, { passive: true }));

    api<{ id: number }>("/sessions", { body: { area, activity, ref_id: refId != null ? String(refId) : null } })
      .then((r) => {
        sessionId = r.id;
        if (stopped) beat(true);
      })
      .catch(() => undefined);

    const beat = (keepalive = false) => {
      if (sessionId == null || active === sent) return;
      sent = active;
      api(`/sessions/${sessionId}/beat`, { body: { active_seconds: active }, keepalive }).catch(() => undefined);
    };

    const tick = window.setInterval(() => {
      if (document.visibilityState === "visible" && Date.now() - lastInteraction.current < IDLE_MS) active += 1;
    }, 1000);
    const beater = window.setInterval(() => beat(), BEAT_MS);
    const onHide = () => document.visibilityState === "hidden" && beat(true);
    document.addEventListener("visibilitychange", onHide);

    return () => {
      stopped = true;
      window.clearInterval(tick);
      window.clearInterval(beater);
      events.forEach((e) => window.removeEventListener(e, touch));
      document.removeEventListener("visibilitychange", onHide);
      beat(true);
    };
  }, [area, activity, refId]);

  /** Marca interacción manualmente (por ejemplo, al llegar la jugada del rival mientras piensas). */
  return () => {
    lastInteraction.current = Date.now();
  };
}
