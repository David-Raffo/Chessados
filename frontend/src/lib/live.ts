// Segundos activos que aún no se han enviado al servidor (useActivity los manda cada 30 s).
// Permite mostrar el tiempo de entrenamiento en vivo, segundo a segundo.

const unsent = new Map<string, number>();
const listeners = new Set<() => void>();
const syncListeners = new Set<() => void>();

const key = (area: string, activity: string) => `${area}|${activity}`;

export function setUnsent(area: string, activity: string, seconds: number) {
  unsent.set(key(area, activity), seconds);
  listeners.forEach((l) => l());
}

/** Segundos sin enviar de un área, opcionalmente solo de ciertas actividades. */
export function unsentFor(area: string, activities?: string[] | null): number {
  let total = 0;
  unsent.forEach((secs, k) => {
    const [a, act] = k.split("|");
    if (a === area && (!activities || activities.includes(act))) total += secs;
  });
  return total;
}

export function onLiveTick(fn: () => void) {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

/** Avisa cuando un envío al servidor ha terminado (para refrescar el progreso). */
export function onSynced(fn: () => void) {
  syncListeners.add(fn);
  return () => {
    syncListeners.delete(fn);
  };
}

export function notifySynced() {
  syncListeners.forEach((l) => l());
}
