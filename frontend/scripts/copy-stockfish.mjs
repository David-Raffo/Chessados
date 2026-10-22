// Copia la build WASM "lite single-thread" de Stockfish a public/stockfish/.
// La versión single-thread no necesita cabeceras COOP/COEP, así que funciona en cualquier servidor.
import { copyFileSync, existsSync, mkdirSync, readdirSync } from "node:fs";
import { join } from "node:path";

const srcDir = join("node_modules", "stockfish", "src");
const outDir = join("public", "stockfish");

if (!existsSync(srcDir)) {
  console.warn("[stockfish] paquete no encontrado, se omite la copia");
  process.exit(0);
}

const files = readdirSync(srcDir);
const js = files.find((f) => /lite-single.*\.js$/.test(f));
const wasm = files.find((f) => /lite-single.*\.wasm$/.test(f));
if (!js || !wasm) {
  console.error("[stockfish] no se encontró la build lite-single en", srcDir, files);
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
// El worker busca el .wasm con su mismo nombre base, así que se copian ambos con nombres a juego.
copyFileSync(join(srcDir, js), join(outDir, "stockfish.js"));
copyFileSync(join(srcDir, wasm), join(outDir, "stockfish.wasm"));
console.log(`[stockfish] copiado ${js} y ${wasm} a ${outDir}`);
