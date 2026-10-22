/**
 * Stockfish 17 (WASM, un hilo) en un Web Worker: juega con límite de ELO sin pasar por el servidor.
 */
/** El motor se cerró (cambio de pantalla, reinicio…): no es un fallo que haya que mostrar. */
export class EngineClosedError extends Error {
  constructor() {
    super("Motor cerrado");
  }
}

export class Engine {
  private worker: Worker;
  private listeners = new Set<(line: string) => void>();
  // Peticiones en curso: al cerrar el motor (o si falla) se rechazan para que nadie se quede esperando
  private pending = new Set<(err: Error) => void>();
  private closed = false;
  private queue: Promise<unknown> = Promise.resolve();
  readonly ready: Promise<void>;

  constructor() {
    this.worker = new Worker("/stockfish/stockfish.js");
    this.worker.onmessage = (e) => {
      const line = String(e.data);
      this.listeners.forEach((l) => l(line));
    };
    this.worker.onerror = () => this.failAll(new Error("El motor ha fallado"));
    this.ready = this.request("uci", "uciok").then(() => this.isReady());
    this.ready.catch(() => undefined); // el error lo recibe quien use el motor
  }

  private failAll(err: Error) {
    this.pending.forEach((reject) => reject(err));
    this.pending.clear();
    this.listeners.clear();
  }

  private send(cmd: string) {
    this.worker.postMessage(cmd);
  }

  /** Envía un comando y espera la primera línea que empiece por `until`. */
  private request(cmd: string, until: string, onLine?: (line: string) => void): Promise<string> {
    return new Promise((resolve, reject) => {
      if (this.closed) {
        reject(new EngineClosedError());
        return;
      }
      const listener = (line: string) => {
        onLine?.(line);
        if (line.startsWith(until)) {
          this.listeners.delete(listener);
          this.pending.delete(reject);
          resolve(line);
        }
      };
      this.listeners.add(listener);
      this.pending.add(reject);
      this.send(cmd);
    });
  }

  private isReady() {
    return this.request("isready", "readyok").then(() => undefined);
  }

  /** Serializa las peticiones: el motor solo piensa una cosa a la vez. */
  private exclusive<T>(fn: () => Promise<T>): Promise<T> {
    const run = this.queue.then(fn, fn);
    this.queue = run.catch(() => undefined);
    return run;
  }

  newGame() {
    return this.exclusive(async () => {
      await this.ready;
      this.send("ucinewgame");
      await this.isReady();
    });
  }

  setOptions(options: [string, string | number][]) {
    return this.exclusive(async () => {
      await this.ready;
      for (const [name, value] of options) this.send(`setoption name ${name} value ${value}`);
      await this.isReady();
    });
  }

  bestMove(fen: string, go: string): Promise<string> {
    return this.exclusive(async () => {
      await this.ready;
      this.send(`position fen ${fen}`);
      const line = await this.request(`go ${go}`, "bestmove");
      return line.split(" ")[1];
    });
  }

  /** Evaluación desde el punto de vista de las blancas (centipeones, mate convertido a ±10000). */
  evaluate(fen: string, depth = 14): Promise<{ cp: number; pv: string[] }> {
    return this.exclusive(async () => {
      await this.ready;
      const whiteToMove = fen.split(" ")[1] === "w";
      let cp = 0;
      let pv: string[] = [];
      this.send(`position fen ${fen}`);
      await this.request(`go depth ${depth}`, "bestmove", (line) => {
        if (!line.startsWith("info") || !line.includes(" pv ")) return;
        const m = line.match(/score (cp|mate) (-?\d+)/);
        if (m) {
          const v = Number(m[2]);
          cp = m[1] === "cp" ? v : Math.sign(v) * (10000 - Math.abs(v));
          if (!whiteToMove) cp = -cp;
        }
        pv = line.split(" pv ")[1].trim().split(" ");
      });
      return { cp, pv };
    });
  }

  terminate() {
    this.closed = true;
    this.worker.terminate();
    this.failAll(new EngineClosedError());
  }
}

/**
 * Fuerza del rival. UCI_Elo tiene un mínimo de 1320; por debajo se combina Skill Level bajo
 * con poca profundidad para que el motor cometa errores de principiante.
 */
export function strengthFor(elo: number): { options: [string, string | number][]; go: (thinkMs: number) => string } {
  if (elo >= 1320) {
    return {
      options: [
        ["UCI_LimitStrength", "true"],
        ["UCI_Elo", Math.min(3190, Math.round(elo))],
        ["Skill Level", 20],
      ],
      go: (ms) => `movetime ${ms}`,
    };
  }
  const t = Math.max(0, Math.min(1, (elo - 400) / 920));
  const depth = 1 + Math.round(t * 4);
  return {
    options: [
      ["UCI_LimitStrength", "false"],
      ["Skill Level", Math.round(t * 5)],
    ],
    go: (ms) => `depth ${depth} movetime ${Math.min(ms, 400)}`,
  };
}
