"""Aprender: cursos de lecciones prácticas, con teoría corta y el tablero delante todo el rato.

Las lecciones están en app/learn_data/, un módulo por curso, cada uno con su lista `LESSONS`.
Cada lección es un dict:
  id, course, title, summary (una frase), minutes, theme (tema de puzzles de Lichess o None),
  steps: lista de pasos.

Tipos de paso (todos llevan `text` y opcionalmente `title`; los de tablero, `fen` y `orientation`):
  explain   → texto con el tablero, flechas y casillas marcadas; `moves` = [{"san", "text"}] permite
              avanzar jugada a jugada con un comentario en cada una.
  select    → pulsar una casilla: `answer`, `success` y `wrong` = {casilla: explicación} para fallos
              concretos. Con "mate": True se comprueba que ir a esa casilla da mate.
  move      → jugar una línea: `line` en SAN inglés, alternando tú y el rival; `hint` tras el primer
              fallo y `success` al acabar. Vale la jugada esperada o cualquier jaque mate.
              `margin` y `min_eval` (centipeones) relajan lo que exige el comprobador en posiciones
              estratégicas, donde la mejor jugada rara vez saca un peón entero a la segunda.
  choice    → `options` = [{"text", "correct", "why"}], exactamente una correcta.
  practice  → `count` puzzles reales de Lichess del tema `theme`.

Formas en el tablero: `arrows` = [origen, destino, color] y `squares` = {casilla: color}, con los
colores de chessground (green, red, blue, yellow).

Antes de publicar, `python -m app.check_learn` comprueba las lecciones con Stockfish.
"""

from .learn_data import aperturas, estrategia, finales, mates, pensar, tactica

# Temario de cada curso: (id, título, tema de puzzles). Las lecciones que aún no existen en
# learn_data se muestran como «próximamente».
COURSES = [
    {
        "id": "mates",
        "title": "Mates de patrón",
        "description": "Los dibujos de mate que hay que reconocer de un vistazo.",
        "outline": [
            ("mate-coz", "El mate de la coz", "smotheredMate"),
            ("mate-ultima-fila", "Mate en la última fila", "backRankMate"),
            ("mate-anastasia", "Mate de Anastasia", "anastasiaMate"),
            ("mate-arabe", "Mate árabe", "arabianMate"),
            ("mate-boden", "Mate de Boden", "bodenMate"),
            ("mate-dos-alfiles", "Mate de los dos alfiles", "doubleBishopMate"),
            ("mate-charretera", "Mate de la charretera", "epauletteMate"),
            ("mate-gancho", "Mate del gancho", "hookMate"),
            ("mate-pillsbury", "Mate de Pillsbury", "pillsburysMate"),
            ("mate-opera", "Mate de la ópera", "operaMate"),
            ("mate-morphy", "Mate de Morphy", "morphysMate"),
            ("mate-cola-golondrina", "Cola de golondrina y cola de milano", "swallowstailMate"),
            ("mate-cerdos-ciegos", "Mate de los cerdos ciegos", "blindSwineMate"),
            ("mate-vukovic", "Mate de Vuković", "vukovicMate"),
        ],
    },
    {
        "id": "tactica",
        "title": "Táctica",
        "description": "Los motivos que deciden las partidas.",
        "outline": [
            ("horquilla", "Horquilla", "fork"),
            ("clavada", "Clavada", "pin"),
            ("enfilada", "Enfilada", "skewer"),
            ("descubierta", "Ataque a la descubierta", "discoveredAttack"),
            ("jaque-doble", "Jaque doble", "doubleCheck"),
            ("desviacion", "Desviación", "deflection"),
            ("atraccion", "Atracción", "attraction"),
            ("eliminar-defensor", "Eliminar al defensor", "capturingDefender"),
            ("interferencia", "Interferencia", "interference"),
            ("rayos-x", "Rayos X", "xRayAttack"),
            ("intermezzo", "Intermezzo", "intermezzo"),
            ("pieza-atrapada", "Pieza atrapada", "trappedPiece"),
            ("despeje", "Despeje", "clearance"),
            ("ataque-f7", "El punto débil: f7 y f2", "attackingF2F7"),
            ("jugada-tranquila", "La jugada tranquila", "quietMove"),
        ],
    },
    {
        "id": "pensar",
        "title": "Cómo pensar",
        "description": "Hábitos que evitan los errores más caros: mirar qué quiere el rival y qué dejas al mover.",
        "outline": [
            ("amenazas-rival", "Las amenazas del rival", "defensiveMove"),
            ("deja-de-defender", "Lo que deja de defender una pieza", "hangingPiece"),
        ],
    },
    {
        "id": "estrategia",
        "title": "Estrategia",
        "description": "Qué hacer cuando no hay táctica.",
        "outline": [
            ("valor-piezas", "Valor de las piezas", None),
            ("alfil-caballo", "Alfil contra caballo", None),
            ("pareja-alfiles", "La pareja de alfiles", None),
            ("alfil-bueno-malo", "Alfil bueno y alfil malo", None),
            ("torres-columnas", "Torres en columnas abiertas", None),
            ("puestos-avanzados", "Puestos avanzados", None),
            ("estructuras-peones", "Estructuras de peones", None),
            ("peon-pasado", "El peón pasado", "advancedPawn"),
            ("espacio-centro", "Espacio y centro", None),
            ("rupturas", "Rupturas de peones", None),
            ("ataque-minorias", "El ataque de minorías", None),
            ("enroques-opuestos", "Enroques opuestos", None),
        ],
    },
    {
        "id": "finales",
        "title": "Finales",
        "description": "Las posiciones que hay que saber ganar (o salvar) de memoria, y cómo jugarlas contra Stockfish.",
        "outline": [
            ("final-dos-torres", "Mate con dos torres", None),
            ("final-dama", "Mate de dama", None),
            ("final-torre", "Mate de torre", None),
            ("final-dos-alfiles", "Mate con dos alfiles", None),
            ("final-alfil-caballo", "Mate de alfil y caballo", None),
            ("final-rey-activo", "El rey, una pieza de ataque", "pawnEndgame"),
            ("final-cuadrado", "La regla del cuadrado", "pawnEndgame"),
            ("final-rey-delante", "El rey delante del peón", "pawnEndgame"),
            ("final-oposicion", "La oposición", "pawnEndgame"),
            ("final-defensa-oposicion", "Defender con la oposición", "pawnEndgame"),
            ("final-bloquear-peon", "Bloquear el peón", "pawnEndgame"),
            ("final-peon-torre", "El peón de torre", "pawnEndgame"),
            ("final-triangulacion", "Triangulación", "pawnEndgame"),
            ("final-zugzwang", "Zugzwang", "zugzwang"),
            ("final-ruptura", "La ruptura de peones", "pawnEndgame"),
            ("final-alejado", "El peón pasado alejado", "pawnEndgame"),
            ("final-caballo-peon", "Caballo contra peón", "knightEndgame"),
            ("final-caballo", "Finales de caballo", "knightEndgame"),
            ("final-color-equivocado", "El alfil del color equivocado", "bishopEndgame"),
            ("final-alfiles-opuestos", "Alfiles de distinto color", "bishopEndgame"),
            ("final-corte-rey", "Cortar al rey con la torre", "rookEndgame"),
            ("final-lucena", "La posición de Lucena", "rookEndgame"),
            ("final-philidor", "La posición de Philidor", "rookEndgame"),
            ("final-torre-detras", "La torre, detrás del peón pasado", "rookEndgame"),
            ("final-torre-activa", "Torre activa, torre pasiva", "rookEndgame"),
            ("final-vancura", "La posición de Vancura", "rookEndgame"),
            ("final-torre-alfil", "Torre contra alfil", "rookEndgame"),
            ("final-dama-peon", "Dama contra peón en séptima", "queenEndgame"),
            ("final-dama-peon-tablas", "Dama contra peón: las tablas", "queenEndgame"),
        ],
    },
    {
        "id": "aperturas",
        "title": "Principios de apertura",
        "description": "Las reglas que valen para cualquier apertura.",
        "outline": [
            ("desarrollo-centro", "Desarrollo y centro", None),
            ("cuando-enrocar", "Cuándo enrocar", None),
            ("dama-pronto", "No saques la dama pronto", None),
            ("trampas", "Trampas típicas", None),
            ("sacrificio-h7", "El sacrificio clásico en h7", None),
            ("rey-centro", "El rey en el centro", None),
        ],
    },
]

# Lecciones de la antigua pantalla «Finales» (app/lessons.py) y su lección equivalente en Aprender
OLD_ENDGAMES = {
    "mate-dos-torres": "final-dos-torres", "mate-dama": "final-dama", "mate-torre": "final-torre",
    "mate-dos-alfiles": "final-dos-alfiles", "mate-alfil-caballo": "final-alfil-caballo",
    "rp-sexta": "final-rey-delante", "rp-oposicion": "final-oposicion", "rp-cuadrado": "final-cuadrado",
    "rp-defensa": "final-defensa-oposicion", "rp-defensa-final": "final-bloquear-peon", "rp-torre": "final-peon-torre",
    "torre-lucena": "final-lucena", "torre-philidor": "final-philidor", "dama-peon": "final-dama-peon",
}

MODULES = {"mates": mates, "tactica": tactica, "pensar": pensar, "estrategia": estrategia, "finales": finales, "aperturas": aperturas}
LESSONS = [lesson for m in MODULES.values() for lesson in m.LESSONS]
BY_ID = {lesson["id"]: lesson for lesson in LESSONS}
