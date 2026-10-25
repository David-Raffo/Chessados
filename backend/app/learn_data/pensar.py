"""Curso «Cómo pensar»: hábitos que evitan los errores más caros. Formato: ver app/learn.py.

Las posiciones salen de partidas reales (puzzles de Lichess, CC0) y de ejemplos comprobados con
Stockfish; la evaluación está en el comentario de cada una.
"""

# Tras 1.e4 e5 2.Ac4 Cc6 3.Dh5: la dama amenaza Dxf7#. …g6 (+0,2) o …De7 (+0,1) defienden; …Cf6?? es mate.
PASTOR = "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3"
# La torre negra ha llegado a e8 y amenaza Te1#. h3 (+7,9) da aire; Dd5?? permite Te1#; Tc8 regala la torre (+3,8).
ULTIMA = "4r1k1/5ppp/8/8/8/3Q4/2R2PPP/6K1 w - - 0 1"
# Lichess 3sE51 antes del error: la dama de d8 defiende la torre de f8. …Db6?? permite Txf8#.
DAMA_ANTES = "r1bq1r1k/pp4pp/8/2Npp3/3n4/6P1/PPP3KP/R2Q1R2 b - - 1 18"
DAMA_TRAS = "r1b2r1k/pp4pp/1q6/2Npp3/3n4/6P1/PPP3KP/R2Q1R2 w - - 2 19"
# Lichess 3FCbh: la torre de g8 defiende d8 por la octava. Posición igualada (−0,4); …Tg5?? permite Dxd8#.
TORRE_ANTES = "1k1r2r1/pp1n1p1p/2pqpp2/Q7/2PP4/P4B1P/1P3PP1/1K1R3R b - - 0 17"
TORRE_TRAS = "1k1r4/pp1n1p1p/2pqpp2/Q5r1/2PP4/P4B1P/1P3PP1/1K1R3R w - - 1 18"
# Lichess 2PWdq: el rey de g8 defiende la torre de f8. …Rh8?? permite Dxf8#; …Tf7 es lo mejor (+0,8 para las negras).
REY_ANTES = "r1b1nrk1/pppq3p/5ppQ/4B3/2B5/8/PPP2PPP/RN4K1 b - - 1 17"
REY_TRAS = "r1b1nr1k/pppq3p/5ppQ/4B3/2B5/8/PPP2PPP/RN4K1 w - - 2 18"

LESSONS = [
    {
        "id": "amenazas-rival",
        "course": "pensar",
        "title": "Las amenazas del rival",
        "summary": "Antes de cada jugada, pregúntate qué quiere hacer el rival. Es el hábito que más partidas salva.",
        "minutes": 8,
        "theme": "defensiveMove",
        "steps": [
            {
                "type": "explain",
                "fen": PASTOR,
                "orientation": "black",
                "title": "Tres preguntas",
                "text": (
                    "La mayoría de las partidas no se pierden por no ver tu plan, sino por no ver el del rival. "
                    "Antes de mover, hazte tres preguntas sobre su última jugada: ¿qué ha cambiado?, ¿qué ataca la "
                    "pieza que acaba de moverse? y ¿qué quiere hacer en su próxima jugada? Aquí la dama blanca acaba "
                    "de llegar a h5."
                ),
                "arrows": [["h5", "f7", "red"], ["c4", "f7", "red"], ["h5", "e5", "yellow"]],
            },
            {
                "type": "select",
                "fen": PASTOR,
                "orientation": "black",
                "title": "¿Qué quiere?",
                "text": "Juegas con negras. Pulsa la casilla donde la dama blanca amenaza dar mate.",
                "answer": "f7",
                "wrong": {
                    "e5": "La dama también ataca el peón de e5 (lo defiende tu caballo), pero hay algo mucho peor.",
                    "e8": "Tu rey está en e8, pero el golpe llega en una casilla de al lado. Mira qué ataca también el alfil de c4.",
                },
                "success": "Exacto: Dxf7 sería mate. La dama y el alfil de c4 atacan f7, y solo lo defiende tu rey.",
            },
            {
                "type": "choice",
                "fen": PASTOR,
                "orientation": "black",
                "title": "La jugada que no puedes hacer",
                "text": "Tres jugadas razonables. Una de ellas pierde en el acto. ¿Cuál?",
                "options": [
                    {"text": "…Cf6, atacando la dama", "correct": True,
                     "why": "¡Exacto! Parece la más natural, porque desarrolla y ataca, pero no hace nada contra la amenaza: Dxf7#."},
                    {"text": "…g6, atacando la dama", "correct": False,
                     "why": "Esta es buena: corta la diagonal de la dama hacia f7 y además la ataca. Stockfish: igualdad."},
                    {"text": "…De7, defendiendo f7", "correct": False,
                     "why": "También vale: la dama defiende f7 y e5 a la vez. Stockfish: igualdad."},
                ],
            },
            {
                "type": "choice",
                "fen": ULTIMA,
                "orientation": "white",
                "title": "Ganando… y en peligro",
                "text": (
                    "Tienes una dama de más y vas ganando claramente. Las negras acaban de llevar su torre a e8. "
                    "¿Qué juegas?"
                ),
                "arrows": [["e8", "e1", "red"]],
                "options": [
                    {"text": "h3: darle una casilla a tu rey", "correct": True,
                     "why": "¡Eso es! La torre amenaza Te1, mate en la última fila. Con h3 tu rey tiene h2 y la amenaza "
                            "desaparece. Stockfish: casi 8 peones de ventaja."},
                    {"text": "Dd5: centralizar la dama", "correct": False,
                     "why": "¡…Te1 mate! Tu rey no tiene casillas y ninguna pieza cubre e1. Con una dama de más, perdida."},
                    {"text": "Tc8: cambiar torres", "correct": False,
                     "why": "Tu torre de c8 no está protegida: …Txc8 y has regalado una torre. Sigues ganando, pero mucho menos."},
                ],
            },
            {
                "type": "explain",
                "fen": ULTIMA,
                "orientation": "white",
                "title": "El hábito",
                "text": (
                    "Fíjate en que nada de esto es táctica difícil: son amenazas de una jugada. Lo que falla es no "
                    "mirar. Antes de mover, mira la última jugada del rival y pregúntate: si ahora pudiera volver a "
                    "mover, ¿qué haría? Si la respuesta es «darme mate» o «comerme algo», atiende eso primero."
                ),
                "squares": {"e1": "red", "h2": "green"},
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales en los que lo importante es defenderse bien, de tu nivel.",
                "theme": "defensiveMove",
                "count": 5,
            },
        ],
    },
    {
        "id": "deja-de-defender",
        "course": "pensar",
        "title": "Lo que deja de defender una pieza",
        "summary": "Toda pieza que mueves deja de defender lo que defendía. Míralo antes de mover, y aprovéchalo cuando lo haga el rival.",
        "minutes": 10,
        "theme": "hangingPiece",
        "steps": [
            {
                "type": "explain",
                "fen": DAMA_ANTES,
                "orientation": "black",
                "title": "Una pieza tiene dos trabajos",
                "text": (
                    "Cada pieza, además de atacar, suele defender algo. Cuando la mueves, ese trabajo queda sin hacer. "
                    "En esta partida real, la dama negra de d8 defiende la torre de f8, que está atacada por la torre "
                    "blanca de f1. Mira lo que pasa cuando la dama se va. (Lichess, puzzle 3sE51)"
                ),
                "arrows": [["d8", "f8", "blue"], ["f1", "f8", "red"]],
                "moves": [
                    {"san": "Qb6", "text": "La dama sale a atacar… y deja de defender f8."},
                    {"san": "Rxf8#", "text": "Mate. La torre de f8 se quedó sola y su captura deja al rey sin casillas."},
                ],
            },
            {
                "type": "select",
                "fen": DAMA_TRAS,
                "orientation": "white",
                "title": "¿Qué se ha quedado sola?",
                "text": "Juegas con blancas. La dama negra acaba de irse a b6. Pulsa la pieza negra que ha dejado sin defensa.",
                "answer": "f8",
                "wrong": {
                    "d4": "El caballo de d4 lo sigue defendiendo la dama desde b6.",
                    "d5": "El peón de d5 también se ha quedado sin la dama, pero hay algo mucho más valioso.",
                    "b6": "Esa es la dama que se ha movido. ¿Qué defendía antes?",
                },
                "success": "Exacto: la torre de f8. Antes la defendía la dama; ahora nadie.",
            },
            {
                "type": "move",
                "fen": DAMA_TRAS,
                "orientation": "white",
                "title": "Castígalo",
                "text": "Aprovecha que la torre de f8 se ha quedado sin defensa.",
                "line": ["Rxf8#"],
                "hint": "Tu torre de f1 se come la de f8.",
                "success": "¡Mate! Y además la torre de f8 cubría la octava fila: al caer, el rey se queda sin salida.",
            },
            {
                "type": "move",
                "fen": TORRE_TRAS,
                "orientation": "white",
                "title": "Otra partida",
                "text": "Las negras acaban de jugar …Tg5 para atacar tu dama. ¿Qué ha dejado de defender esa torre? (Lichess, puzzle 3FCbh)",
                "line": ["Qxd8#"],
                "hint": "Antes de moverse, la torre de g8 defendía toda la octava fila.",
                "success": "¡Mate! La torre de g8 defendía d8 por la octava fila; al irse a g5, d8 quedó colgando.",
            },
            {
                "type": "move",
                "fen": REY_TRAS,
                "orientation": "white",
                "title": "Hasta el rey defiende",
                "text": "El rey negro acaba de esconderse en h8. ¿Qué defendía en g8? (Lichess, puzzle 2PWdq)",
                "line": ["Qxf8#"],
                "hint": "Mira la torre de f8.",
                "success": "¡Mate! El rey defendía la torre de f8; al irse a la esquina, la dama se la come con mate.",
            },
            {
                "type": "choice",
                "fen": TORRE_ANTES,
                "orientation": "black",
                "title": "Ahora te toca a ti",
                "text": (
                    "Esta es la posición de antes de …Tg5, con negras. Está igualada. Tu torre de g8 parece no hacer "
                    "nada y te apetece activarla con …Tg5, atacando la dama. ¿Lo haces?"
                ),
                "options": [
                    {"text": "Sí: ataca la dama y activa la torre", "correct": False,
                     "why": "Es justo lo que pasó en la partida: Dxd8#. La torre de g8 sí hacía algo: defendía d8."},
                    {"text": "No: la torre de g8 está defendiendo d8", "correct": True,
                     "why": "Eso es. Antes de mover una pieza, mira qué defiende. Con …f5 o …c5 la posición sigue igualada."},
                ],
            },
            {
                "type": "choice",
                "fen": REY_ANTES,
                "orientation": "black",
                "title": "El rey quiere esconderse",
                "text": "Con negras: la dama blanca está muy cerca de tu rey. ¿Qué juegas?",
                "options": [
                    {"text": "…Rh8: el rey a la esquina, más seguro", "correct": False,
                     "why": "¡Dxf8 mate! El rey defendía la torre de f8 desde g8: al apartarse, la deja sola."},
                    {"text": "…Tf7: defender la séptima con la torre", "correct": True,
                     "why": "Bien: la torre se aparta de la dama y protege f7 y h7. Stockfish la prefiere claramente a todo lo demás."},
                    {"text": "…Df7: cambiar el sitio de la dama", "correct": False,
                     "why": "¡El alfil de c4 apunta a f7! Axf7+ y te has quedado sin dama por un alfil. Stockfish: casi 5 peones de ventaja blanca."},
                ],
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con piezas que se quedaron sin defensa, de tu nivel.",
                "theme": "hangingPiece",
                "count": 5,
            },
        ],
    },
]
