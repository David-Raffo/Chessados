"""Aprender: cursos de lecciones prácticas, con teoría corta y el tablero delante todo el rato.

Cada lección es una lista de pasos:
  explain   → texto con el tablero, flechas y casillas marcadas; `moves` permite avanzar jugada a jugada.
  select    → pulsar una casilla (`answer`); `wrong` da una explicación para fallos concretos.
  move      → jugar una línea (`line`, en SAN, alternando tú y el rival). Vale la jugada esperada o
              cualquier jaque mate. `hint` se muestra tras el primer fallo.
  choice    → elegir una opción; cada una explica por qué es correcta o no.
  practice  → `count` puzzles reales de Lichess del tema `theme`.

Las posiciones y soluciones se comprueban con Stockfish (profundidad 24): en cada jugada tuya, la
esperada es la única que da el mate más rápido.

Formas en el tablero: `arrows` = [origen, destino, color] y `squares` = {casilla: color}, con los
colores de chessground (green, red, blue, yellow).
"""

LESSONS = [
    {
        "id": "mate-coz",
        "course": "mates",
        "title": "El mate de la coz",
        "summary": "Un caballo da mate a un rey encerrado por sus propias piezas.",
        "minutes": 10,
        "theme": "smotheredMate",
        "steps": [
            {
                "type": "explain",
                "fen": "6rk/5Npp/8/8/8/8/6PP/6K1 b - - 0 1",
                "orientation": "white",
                "title": "Ahogado por los suyos",
                "text": (
                    "El rey negro está en jaque y no puede moverse: g8, g7 y h7 están ocupadas por sus "
                    "propias piezas. El caballo da jaque saltando, así que tampoco se puede tapar. "
                    "Es el mate de la coz, también llamado mate ahogado."
                ),
                "arrows": [["f7", "h8", "green"]],
                "squares": {"g8": "red", "g7": "red", "h7": "red"},
            },
            {
                "type": "select",
                "fen": "6rk/6pp/8/6N1/8/8/6PP/6K1 w - - 0 1",
                "orientation": "white",
                "title": "Encuentra la casilla",
                "text": "El rey negro ya está encerrado. ¿A qué casilla tiene que saltar el caballo para dar mate? Púlsala.",
                "answer": "f7",
                "wrong": {
                    "e6": "Desde e6 el caballo no ataca h8.",
                    "h7": "Capturar el peón de h7 no da jaque: desde h7 el caballo no ataca h8.",
                    "f3": "Desde f3 el caballo no ataca h8.",
                    "e4": "Desde e4 el caballo no ataca h8.",
                    "h3": "Desde h3 el caballo no ataca h8.",
                },
                "success": "Exacto: desde f7 el caballo ataca h8 y el rey no tiene adónde ir.",
            },
            {
                "type": "move",
                "fen": "6rk/6pp/8/6N1/8/8/6PP/6K1 w - - 0 1",
                "orientation": "white",
                "title": "Ahora, dalo tú",
                "text": "Juega el mate.",
                "line": ["Nf7#"],
                "hint": "El caballo de g5 salta a f7.",
                "success": "¡Mate! Fíjate en que la torre de g8 es la que le quita la última casilla a su rey.",
            },
            {
                "type": "move",
                "fen": "kr6/pp6/8/3N4/8/8/PP6/K7 w - - 0 1",
                "orientation": "white",
                "title": "En el otro flanco",
                "text": "El patrón funciona igual en cualquier esquina. Da mate.",
                "line": ["Nc7#"],
                "hint": "Busca la casilla desde la que el caballo ataca a8.",
                "success": "Mate. Rey en la esquina, rodeado de sus piezas y un caballo que llega: siempre el mismo dibujo.",
            },
            {
                "type": "choice",
                "fen": "6rk/6p1/7p/6N1/8/8/6PP/6K1 w - - 0 1",
                "orientation": "white",
                "title": "¿Funciona aquí?",
                "text": "Las negras han movido su peón a h6. ¿Es Cf7+ mate?",
                "options": [
                    {"text": "Sí, es mate", "correct": False,
                     "why": "No: con el peón en h6, la casilla h7 ha quedado libre y el rey escapa por ahí."},
                    {"text": "No, el rey escapa a h7", "correct": True,
                     "why": "Eso es. El mate de la coz necesita que el rey no tenga ninguna casilla libre."},
                    {"text": "No, la torre captura el caballo", "correct": False,
                     "why": "La torre de g8 no puede capturar en f7: se mueve en línea recta."},
                ],
            },
            {
                "type": "explain",
                "fen": "4r2k/6pp/8/6N1/2Q5/8/5PPP/6K1 w - - 0 1",
                "orientation": "white",
                "title": "El legado de Philidor",
                "text": (
                    "Lo normal es que el rey no esté encerrado desde el principio: hay que encerrarlo. "
                    "La combinación clásica usa la dama y el caballo. Avanza jugada a jugada."
                ),
                "moves": [
                    {"san": "Nf7+", "text": "Jaque de caballo. El rey solo puede ir a g8."},
                    {"san": "Kg8", "text": "Forzado."},
                    {"san": "Nh6+", "text": "¡Jaque doble! Dan jaque el caballo y la dama a la vez, así que el rey tiene que moverse."},
                    {"san": "Kh8", "text": "Si fuera a f8, Df7 sería mate. Vuelve a la esquina."},
                    {"san": "Qg8+", "text": "El golpe: la dama se sacrifica en g8. El rey no puede capturarla porque la protege el caballo."},
                    {"san": "Rxg8", "text": "La torre tiene que capturar… y ella misma cierra la última casilla de su rey."},
                    {"san": "Nf7#", "text": "Mate de la coz. La dama se ha sacrificado para que la torre negra encierre a su propio rey."},
                ],
            },
            {
                "type": "move",
                "fen": "4r2k/6pp/8/6N1/2Q5/8/5PPP/6K1 w - - 0 1",
                "orientation": "white",
                "title": "Ahora tú, sin ayuda",
                "text": "Las negras amenazan Te1, que sería mate. No hay tiempo para nada que no sea jaque: da mate en 4.",
                "line": ["Nf7+", "Kg8", "Nh6+", "Kh8", "Qg8+", "Rxg8", "Nf7#"],
                "hint": "Empieza con jaque de caballo en f7.",
                "success": "¡Perfecto! Jaque, jaque doble, sacrificio y mate: el legado de Philidor.",
            },
            {
                "type": "move",
                "fen": "5r1k/pp4pp/4Q3/6N1/8/1B6/5PPP/6K1 w - - 0 1",
                "orientation": "white",
                "title": "Atajo",
                "text": "Aquí el rey ya está en la esquina. Da mate en 2.",
                "line": ["Qg8+", "Rxg8", "Nf7#"],
                "hint": "Sacrifica la dama en g8: el alfil de b3 la protege.",
                "success": "Mate. El alfil de b3 protegía g8, así que la única respuesta era Txg8 y su propia torre encerró al rey.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales de Lichess con el mate de la coz, de tu nivel.",
                "theme": "smotheredMate",
                "count": 5,
            },
        ],
    },
]

# Temario de cada curso: las lecciones que aún no existen se muestran como «próximamente»
COURSES = [
    {
        "id": "mates",
        "title": "Mates de patrón",
        "description": "Los dibujos de mate que hay que reconocer de un vistazo.",
        "outline": [
            ("mate-coz", "El mate de la coz"),
            (None, "Mate en la última fila"),
            (None, "Mate de Anastasia"),
            (None, "Mate árabe"),
            (None, "Mate de Boden"),
            (None, "Mate de los dos alfiles"),
            (None, "Mate de la charretera"),
            (None, "Mate del gancho"),
            (None, "Mate de Pillsbury"),
            (None, "Mate de la ópera"),
            (None, "Mate de Morphy"),
            (None, "Cola de golondrina y cola de milano"),
            (None, "Mate de los cerdos ciegos"),
            (None, "Mate de Vuković"),
        ],
    },
    {
        "id": "tactica",
        "title": "Táctica",
        "description": "Los motivos que deciden las partidas.",
        "outline": [(None, t) for t in (
            "Horquilla", "Clavada", "Enfilada", "Ataque a la descubierta", "Jaque doble", "Desviación",
            "Atracción", "Eliminar al defensor", "Interferencia", "Rayos X", "Intermezzo", "Pieza atrapada",
        )],
    },
    {
        "id": "estrategia",
        "title": "Estrategia",
        "description": "Qué hacer cuando no hay táctica.",
        "outline": [(None, t) for t in (
            "Valor de las piezas", "Alfil contra caballo", "La pareja de alfiles", "Alfil bueno y alfil malo",
            "Torres en columnas abiertas", "Puestos avanzados", "Estructuras de peones", "El peón pasado",
        )],
    },
    {
        "id": "aperturas",
        "title": "Principios de apertura",
        "description": "Las reglas que valen para cualquier apertura.",
        "outline": [(None, t) for t in (
            "Desarrollo y centro", "Cuándo enrocar", "No saques la dama pronto", "Trampas típicas",
        )],
    },
]

BY_ID = {lesson["id"]: lesson for lesson in LESSONS}
