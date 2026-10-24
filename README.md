# Chessados · entrenador personal de ajedrez

App web autoalojada en Docker: juegas, entrenas y la app mide qué haces y te dice qué toca a continuación.
Todo corre en tu máquina, con motor (Stockfish) y datos (puzzles de Lichess, CC0) de código abierto.

## Arrancar

```bash
cp .env.example .env   # opcional: cambia JWT_SECRET y contraseñas
docker compose up -d --build
```

Abre <http://localhost:8080> y crea una cuenta. Cada persona de casa puede tener la suya.

La primera vez, el contenedor `importer` descarga en streaming los puzzles de Lichess y guarda
1 millón de los bien valorados y muy jugados (tarda unos minutos). Para cambiarlo, ajusta `PUZZLE_LIMIT`
en `.env` (`0` = todos los que pasan el filtro) y ejecuta `docker compose run --rm importer`: solo añade
los que falten. También puedes dejar el fichero
`lichess_db_puzzle.csv.zst` en `data/` para no descargarlo.

## Qué incluye

| Módulo | Qué hace |
|---|---|
| Jugar | Stockfish 17.1 en el navegador (ELO 400–3000, modo Escalera +50/−25) o Maia 1100–1900 (juego humano, lc0). Relojes 15+10, 30+0, 10+5 y 5+3 |
| Revisión | Primero anotas tus dudas, después el motor: gráfica de evaluación, imprecisión/error/error grave, mejor jugada con flecha, línea principal, precisión y desviación del repertorio |
| Puzzles | Base de Lichess con ELO propio, filtros por tema, pistas y cola de repaso de fallos (1, 3, 7 y 21 días) |
| Aprender | 76 lecciones prácticas en 5 cursos (mates de patrón, táctica, estrategia, finales y principios de apertura): teoría corta con el tablero, ejercicios de pulsar, elegir y jugar, partidas contra Stockfish y puzzles reales del tema. Comprobadas con Stockfish (`docker compose exec worker python -m app.check_learn`) |
| Contrarreloj | 3 o 5 minutos, dificultad creciente, tres fallos y fuera, récord y gráfica |
| Finales | 14 lecciones teóricas (mates básicos, rey y peón, oposición, Lucena, Philidor…) contra Stockfish a máxima fuerza, con ELO de finales y repaso espaciado |
| Aperturas | Repertorio propio en árbol, entrenamiento SM-2, nombres de `chess-openings` y detección de dónde te sales en tus partidas |
| Woodpecker | Bloques de 100–300 puzzles en ciclos cada vez más cortos |
| Desafíos diarios | Puzzle del día y «encuentra la mejor jugada» en tus propias partidas; mantienen la racha |
| Entrenador | Reglas 1–5 de la guía, sesión «Entrenar hoy» e informe semanal |
| Progreso | Curvas de ELO, mapa de calor, horas frente a objetivo, radar de temas y errores por fase |

Importa partidas de Lichess, Chess.com o pegando PGN. La app es instalable como PWA y usable desde el móvil.

## Arquitectura

```
navegador ── React + Vite + TS, Tailwind, chessground, chess.js, Recharts
   │          Stockfish 17.1 WASM para jugar sin latencia
   ▼
web (nginx) ──/api──► api (FastAPI, python-chess, SQLAlchemy)
                          │
worker (Stockfish nativo) ┼──► db (PostgreSQL 16, volumen pgdata)
importer (una vez)  ──────┤
maia (lc0 + Maia) ◄───────┘
```

- `backend/app/main.py` — API y creación de tablas.
- `backend/app/worker.py` — cola de análisis en PostgreSQL (`FOR UPDATE SKIP LOCKED`), profundidad `ANALYSIS_DEPTH`.
- `backend/app/coach.py` — reglas del entrenador y plan del día.
- `backend/app/glicko2.py` — Glicko-2 (el sistema de Lichess).
- `backend/app/lessons.py` — lecciones de finales (posiciones comprobadas con Stockfish).
- `maia/` — servicio con lc0 y las redes Maia; la primera compilación tarda unos minutos.
- `frontend/src/pages/` — una página por pantalla; `components/Board.tsx` es el tablero común.

## Desarrollo del frontend

Con el stack de Docker levantado:

```bash
cd frontend && npm install && npm run dev
```

Vite sirve en <http://localhost:5173> y redirige `/api` a `http://localhost:8080`.
