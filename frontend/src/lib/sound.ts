import { prefs } from "./prefs";

// Sonidos sintetizados con WebAudio: sin ficheros de audio que descargar
let ctx: AudioContext | null = null;

function tone(freq: number, duration: number, type: OscillatorType = "sine", gain = 0.07, delay = 0) {
  if (!prefs.sound) return;
  try {
    ctx ??= new AudioContext();
    const t = ctx.currentTime + delay;
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    g.gain.setValueAtTime(gain, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + duration);
    osc.connect(g).connect(ctx.destination);
    osc.start(t);
    osc.stop(t + duration);
  } catch {
    /* audio no disponible */
  }
}

export const sound = {
  move: () => tone(330, 0.07, "triangle", 0.09),
  capture: () => {
    tone(220, 0.09, "square", 0.05);
    tone(160, 0.08, "triangle", 0.06, 0.02);
  },
  check: () => tone(660, 0.12, "sawtooth", 0.03),
  good: () => {
    tone(523, 0.1, "sine", 0.08);
    tone(784, 0.16, "sine", 0.08, 0.09);
  },
  bad: () => tone(150, 0.25, "sawtooth", 0.04),
  end: () => {
    tone(392, 0.12, "triangle", 0.08);
    tone(523, 0.12, "triangle", 0.08, 0.12);
    tone(659, 0.25, "triangle", 0.08, 0.24);
  },
};
