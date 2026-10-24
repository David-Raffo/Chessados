"""Curso «Finales» (finales teóricos nuevos). Formato de las lecciones: ver app/learn.py.

Cada posición se comprobó con Stockfish (profundidad 20); la evaluación va en su comentario. Las de
partidas reales son puzzles de Lichess (CC0) y se indica su número.
"""

# --- Finales de peones -------------------------------------------------------------------
# El rey blanco llega antes a los peones negros: Rd6 (+8,8) frente a Rc5 o a4 (+6).
REY_ACTIVO = "8/pp4k1/8/3K4/8/8/PP6/8 w - - 0 1"
# Trébuchet: zugzwang mutuo. Con blancas a mover pierden (−5,2); con negras a mover, ganan las blancas (+8,2).
TREBUCHET_B = "8/8/8/3Kp3/4Pk2/8/8/8 b - - 0 1"
TREBUCHET_W = "8/8/8/3Kp3/4Pk2/8/8/8 w - - 0 1"
# Lichess 5YVVa: f4!, el rey negro se queda sin jugadas buenas (+5,5; cualquier otra pierde).
ZZ_REAL = "8/8/5p2/7k/4P2p/5P1K/8/8 w - - 2 58"
# Ruptura 3 contra 3: b6! gana (+5,2); a6 o c6 pierden.
RUPTURA = "6k1/ppp5/8/PPP5/8/8/8/6K1 w - - 0 1"
# Lichess FAngI: a6! bxa6 c6 y el peón de c corona (+5,0).
RUPTURA_REAL = "8/pp6/8/P1P5/1Pk4p/8/6K1/8 w - - 1 43"
# Triangulación: con negras a mover pierden (M23); con blancas a mover, Ra5 o Ra7 ganan (+8,8)
# perdiendo un tiempo en triángulo, y Rb5? es tablas (el negro copia con Rb7).
TRIANGULO = "8/2k5/K2p4/3P4/8/8/8/8 w - - 0 1"
TRIANGULO_B = "8/2k5/K2p4/3P4/8/8/8/8 b - - 0 1"
# Peón pasado alejado: las blancas ganan (+8).
ALEJADO = "8/8/4k1p1/7p/P3K2P/6P1/8/8 w - - 0 1"
# Lichess 0NwPP: cxb5! axb5 a5 crea el pasado alejado (+5,2; axb5 es tablas).
ALEJADO_REAL = "8/7p/p7/1pk1p3/P1P4P/1K2P3/8/8 w - - 0 40"

# --- Caballos y alfiles ----------------------------------------------------------------
# Caballo contra peón: Cd3 o Cf3 aguantan (0,0); con el rey, el peón corona (−4).
CAB_PEON = "8/8/8/8/8/1p6/k7/4N1K1 w - - 0 1"
# Lichess Ck6yo: Cb5+! desvía el caballo negro y el peón de a corona (+6,3).
CAB_REAL = "8/P1n3pp/3N4/8/2pk4/3p4/5PPP/4K3 w - - 4 44"
# Rey, caballo y peón contra rey: gana (+8,5).
CAB_GANA = "8/8/8/4k3/8/2N1K3/3P4/8 w - - 0 1"
# Alfil del color equivocado: con el alfil de claras y peón de h, tablas si el rey llega a h8 (−0,4);
# …Re7?? pierde. Con el alfil de oscuras, mate (M22).
COLOR_EQ = "8/5k2/8/3K3P/2B5/8/8/8 b - - 0 1"
COLOR_OK = "8/5k2/8/3K3P/3B4/8/8/8 b - - 0 1"
# Alfiles de distinto color: dos peones de más y tablas (+0,1).
OPUESTOS = "8/4k3/3b4/3P1P2/2B1K3/8/8/8 w - - 0 1"

# --- Torres ------------------------------------------------------------------------------
# La torre de d1 corta al rey negro: Re3 gana (+4,6); e5? (0,0) y Tc1+? (0,0) lo dejan escapar.
CORTE = "6r1/8/8/8/2k1P3/8/5K2/3R4 w - - 0 1"
# Torre contra peón: Td1 gana (+4,5); Te1? o Tb4? son tablas.
CORTE_PEON = "8/8/1K6/8/3p4/5k2/8/1R6 w - - 0 1"
# Torre contra peón para jugar: gana (+5).
CORTE_JUGAR = "8/8/8/8/K2p4/6k1/8/1R6 w - - 0 1"
# Torre detrás del pasado propio (+5,2) frente a torre delante (+0,5).
DETRAS = "r7/5pk1/P5p1/7p/7P/6P1/5PK1/R7 w - - 0 1"
DELANTE = "R7/P4pk1/6p1/7p/7P/6P1/5PK1/r7 w - - 0 1"
# Torre detrás del peón rival: Td8+ gana (+5,0); Tf8? es tablas.
DETRAS_RIVAL = "2R5/8/8/8/2K5/2p5/3k4/8 w - - 0 1"
# Torre activa con un peón de menos: tablas (+0,2).
ACTIVA = "8/5pk1/6p1/R6p/P6P/6P1/r4PK1/8 w - - 0 1"
# Vancura: torre negra lateral en f6, tablas (0,0).
VANCURA = "R7/6k1/P4r2/8/8/8/8/6K1 b - - 0 1"
# Torre contra alfil: rey en la esquina del color contrario al alfil, tablas (−0,3).
TORRE_ALFIL = "6bk/4R3/6K1/8/8/8/8/8 b - - 0 1"

# --- Damas -------------------------------------------------------------------------------
# Dama contra peón de alfil en séptima con el rey blanco lejos: tablas (0,0).
DAMA_ALFIL = "8/8/8/8/8/8/1kp5/6KQ w - - 0 1"
# Dama contra peón de torre: tablas (0,0).
DAMA_TORRE = "8/8/8/8/8/8/pk6/6KQ w - - 0 1"
# Dama contra peón central: gana (M17).
DAMA_CENTRAL = "8/8/8/8/8/8/2kp4/6KQ w - - 0 1"

LESSONS = [
    {
        "id": "final-rey-activo",
        "course": "finales",
        "title": "El rey, una pieza de ataque",
        "summary": "En el final el rey sale de su escondite y pelea. El que llega antes, gana.",
        "minutes": 9,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": REY_ACTIVO,
                "orientation": "white",
                "title": "Cambio de papel",
                "text": (
                    "En el medio juego escondes al rey; en el final, sin damas, es una pieza fuerte que vale más o menos "
                    "como una torre. Aquí los peones están igualados, pero tu rey está a dos pasos de los peones negros y "
                    "el negro, en g7, a cinco. Eso decide la partida."
                ),
                "arrows": [["d5", "c6", "green"], ["c6", "b7", "green"], ["g7", "c7", "red"]],
                "squares": {"a7": "red", "b7": "red"},
            },
            {
                "type": "choice",
                "fen": REY_ACTIVO,
                "orientation": "white",
                "title": "El camino más corto",
                "text": "¿Por dónde lleva tu rey a los peones negros?",
                "options": [
                    {"text": "Rd6, camino de c7", "correct": True,
                     "why": "Exacto: desde d6 amenaza Rc7 y Rxb7, y el rey negro no llega a tiempo. Stockfish: ganas con más de 8 peones de ventaja."},
                    {"text": "Rc4, para vigilar tus peones primero", "correct": False,
                     "why": "Parece prudente, pero pierdes el tiempo que te sobraba: el rey negro llega a defender y son tablas (Stockfish: 0,00)."},
                    {"text": "a4, avanzar los peones", "correct": False,
                     "why": "Sigue ganando, pero regalas tiempo: Stockfish baja de +8 a unos +5. Tus peones no corren peligro; primero el rey."},
                ],
            },
            {
                "type": "choice",
                "fen": REY_ACTIVO,
                "orientation": "white",
                "title": "¿Y los peones?",
                "text": "En un final de peones, ¿qué suele ir primero: mover peones o activar el rey?",
                "options": [
                    {"text": "Activar el rey", "correct": True,
                     "why": "Casi siempre. Los peones no se pueden mover hacia atrás: cada avance es un compromiso. El rey, "
                            "en cambio, mejora y amenaza sin crear debilidades."},
                    {"text": "Avanzar los peones cuanto antes", "correct": False,
                     "why": "Un peón que avanza sin apoyo es un blanco fácil para el rey rival."},
                ],
            },
            {
                "type": "play",
                "fen": REY_ACTIVO,
                "orientation": "white",
                "title": "Ahora, gánalo",
                "text": "Cómete los peones negros con tu rey, corona uno de los tuyos y gana.",
                "goal": "win",
                "moves": 40,
                "hint": "Rey a c7 y a b7: primero los peones negros, luego avanza los tuyos con el rey delante.",
                "success": "Así se juegan los finales de peones: el rey manda.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de peones de partidas reales, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-triangulacion",
        "course": "finales",
        "title": "Triangulación",
        "summary": "Tu rey da un rodeo en triángulo para pasarle el turno al rival.",
        "minutes": 9,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": TRIANGULO,
                "orientation": "white",
                "title": "Ojalá le tocara a él",
                "text": (
                    "Tu rey quiere llegar a d6 para comerse el peón. Si aquí le tocara mover al negro, tendría que soltar "
                    "c7 y tu rey entraría por b7 o b6. Pero te toca a ti, y desde a6 no tienes por dónde avanzar."
                ),
                "arrows": [["a6", "b7", "green"], ["b7", "c6", "green"], ["c6", "d6", "green"]],
                "squares": {"c7": "red", "d6": "red"},
            },
            {
                "type": "choice",
                "fen": TRIANGULO_B,
                "orientation": "white",
                "title": "Le toca al negro",
                "text": "Misma posición, pero mueven las negras. ¿Qué pasa?",
                "options": [
                    {"text": "Las negras pierden", "correct": True,
                     "why": "Eso es: cualquier jugada del rey negro deja pasar al tuyo hacia d6. Stockfish ve mate. Es un zugzwang."},
                    {"text": "Tablas", "correct": False,
                     "why": "No: el rey negro está atado a c7 y cualquier paso le abre la puerta al tuyo."},
                ],
            },
            {
                "type": "explain",
                "fen": TRIANGULO,
                "orientation": "white",
                "title": "El triángulo",
                "text": (
                    "La solución: perder un tiempo. Tu rey tiene tres casillas en triángulo (a6, a5 y b5) y el negro no tiene "
                    "un triángulo igual para contestar. Avanza jugada a jugada."
                ),
                "moves": [
                    {"san": "Ka5", "text": "Primer lado del triángulo."},
                    {"san": "Kb7", "text": "El negro se aleja de c7, pero vuelve."},
                    {"san": "Kb5", "text": "Segundo lado."},
                    {"san": "Kc7", "text": "El rey negro vuelve a su sitio."},
                    {"san": "Ka6", "text": "Y tu rey también. Misma posición… pero ahora le toca al negro."},
                ],
                "squares": {"a6": "green", "a5": "green", "b5": "green"},
            },
            {
                "type": "choice",
                "fen": TRIANGULO,
                "orientation": "white",
                "title": "¿Por qué no Rb5?",
                "text": "Rb5 parece la jugada natural. ¿Qué pasa si la juegas?",
                "options": [
                    {"text": "El negro responde Rb7 y copia todos tus movimientos", "correct": True,
                     "why": "Exacto: Rb5 Rb7, Ra5 Ra7, Rb5 Rb7… tablas. Solo el triángulo le pasa el turno. Stockfish: Rb5 es 0,00."},
                    {"text": "Gana igual, solo que más despacio", "correct": False,
                     "why": "No: con Rb5 el negro coge la oposición y ya no la suelta. Son tablas."},
                ],
            },
            {
                "type": "play",
                "fen": TRIANGULO,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Triangula, cómete el peón de d6 y corona.",
                "goal": "win",
                "moves": 25,
                "hint": "Primero Ra5 (o Ra7) para perder un tiempo; cuando el negro tenga que mover, entra hacia d6.",
                "success": "Has ganado gracias a un rodeo de tres jugadas: así se usa la triangulación.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de peones de partidas reales, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-zugzwang",
        "course": "finales",
        "title": "Zugzwang",
        "summary": "Cuando cualquier jugada empeora tu posición, tener que mover es una desgracia.",
        "minutes": 9,
        "theme": "zugzwang",
        "steps": [
            {
                "type": "explain",
                "fen": TREBUCHET_W,
                "orientation": "white",
                "title": "Obligado a mover",
                "text": (
                    "Zugzwang es una palabra alemana: «obligación de mover». En ajedrez no se puede pasar, y a veces "
                    "eso mata. Aquí cada rey ataca el peón rival y defiende el suyo. El que mueva tiene que soltar su "
                    "peón: es un zugzwang mutuo, el famoso «trébuchet»."
                ),
                "arrows": [["d5", "e5", "red"], ["f4", "e4", "red"]],
                "squares": {"e4": "yellow", "e5": "yellow"},
            },
            {
                "type": "choice",
                "fen": TREBUCHET_W,
                "orientation": "white",
                "title": "Te toca a ti",
                "text": "En esta posición les toca mover a las blancas. ¿Qué pasa?",
                "options": [
                    {"text": "Las blancas pierden", "correct": True,
                     "why": "Eso es. El rey blanco tiene que apartarse, el negro se come e4 y luego corona. Stockfish: −5."},
                    {"text": "Las blancas ganan: atacan primero", "correct": False,
                     "why": "Atacar primero no sirve: el rey blanco no puede comer e5 porque lo defiende el rey negro."},
                    {"text": "Tablas: nadie puede hacer nada", "correct": False,
                     "why": "Alguien tiene que mover, y el que mueve suelta su peón."},
                ],
            },
            {
                "type": "play",
                "fen": TREBUCHET_B,
                "orientation": "white",
                "title": "Esta vez mueven ellas",
                "text": "Misma posición, pero le toca al negro. Aprovecha el zugzwang y gana.",
                "goal": "win",
                "moves": 25,
                "color": "white",
                "hint": "En cuanto el rey negro suelte e5, cómetelo y escolta tu peón con el rey delante.",
                "success": "Zugzwang convertido en victoria: no hiciste nada… salvo esperar a que el rival tuviera que mover.",
            },
            {
                "type": "move",
                "fen": ZZ_REAL,
                "orientation": "white",
                "title": "De una partida real",
                "text": "Una jugada de peón tranquila deja al rey negro sin buenas casillas. Encuéntrala. (Lichess, puzzle 5YVVa)",
                "line": ["f4"],
                "min_eval": 150,
                "hint": "Un peón tuyo puede avanzar y quitarle al rey negro las casillas g5 y g4… sin dejar nada colgando.",
                "success": "Exacto: tras f4 el rey negro no tiene jugadas buenas, tendrá que retirarse y el peón de h4 caerá. Cualquier otra jugada perdía.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de zugzwang de partidas reales, de tu nivel.",
                "theme": "zugzwang",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-ruptura",
        "course": "finales",
        "title": "La ruptura de peones",
        "summary": "Tres peones contra tres, y uno se cuela a coronar a base de sacrificios.",
        "minutes": 9,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": RUPTURA,
                "orientation": "white",
                "title": "El truco más bonito",
                "text": (
                    "Tres peones contra tres, frente a frente. Parece que nada se mueve… pero si los reyes están lejos, "
                    "las blancas ganan con una ruptura: sacrifican dos peones para que el tercero corone. Avanza jugada a jugada."
                ),
                "moves": [
                    {"san": "b6", "text": "¡El peón del centro primero! Amenaza bxa7 o bxc7."},
                    {"san": "cxb6", "text": "Si toma con el de c…"},
                    {"san": "a6", "text": "…el de a se ofrece."},
                    {"san": "bxa6", "text": "Lo toma."},
                    {"san": "c6", "text": "Y el de c ya no tiene a nadie delante."},
                    {"san": "Kf7", "text": "El rey negro llega tarde."},
                    {"san": "c7", "text": "Una casilla más…"},
                    {"san": "Ke7", "text": "…y no alcanza c8."},
                    {"san": "c8=Q", "text": "Dama. Dos peones sacrificados para coronar el tercero."},
                ],
            },
            {
                "type": "choice",
                "fen": RUPTURA,
                "orientation": "white",
                "title": "Por dónde empezar",
                "text": "¿Con qué peón empieza la ruptura?",
                "options": [
                    {"text": "b6, el del centro", "correct": True,
                     "why": "Eso es. Atacando los dos peones a la vez, uno de tus peones de los lados queda libre pase lo que pase."},
                    {"text": "a6, el del borde", "correct": False,
                     "why": "Tras …bxa6 y bxa6 (o c6), las negras recapturan y te quedas sin ruptura. Stockfish: pierdes."},
                    {"text": "c6, el otro lado", "correct": False,
                     "why": "Tras …bxc6, el peón negro de c6 frena todo. La ruptura empieza por el centro."},
                ],
            },
            {
                "type": "move",
                "fen": RUPTURA_REAL,
                "orientation": "white",
                "title": "De una partida real",
                "text": "Otra ruptura: dos peones tuyos contra uno, y el rey negro no llega. (Lichess, puzzle FAngI)",
                "line": ["a6"],
                "hint": "Sacrifica el peón de a para abrir paso al de c.",
                "success": "¡Eso es! Si …bxa6, c6 y el peón de c corre hasta c8: el rey negro de b4 no llega.",
            },
            {
                "type": "play",
                "fen": RUPTURA,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Haz la ruptura, corona y da mate con la dama.",
                "goal": "win",
                "moves": 35,
                "hint": "Empieza con b6 y, según tome el negro, sacrifica el peón del lado contrario.",
                "success": "Ruptura, coronación y mate: la combinación de peones más famosa del ajedrez.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de peones de partidas reales, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-alejado",
        "course": "finales",
        "title": "El peón pasado alejado",
        "summary": "Un peón pasado lejos del resto arrastra al rey rival a una esquina.",
        "minutes": 9,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": ALEJADO,
                "orientation": "white",
                "title": "Un señuelo",
                "text": (
                    "Tu peón de a4 está solo en su flanco. Las negras tienen que pararlo con el rey, y mientras su rey "
                    "va a por él, el tuyo se come los peones del otro lado. Muchas veces el peón alejado gana aunque "
                    "acabe sacrificado."
                ),
                "arrows": [["a4", "a8", "green"], ["e4", "g6", "blue"]],
                "squares": {"a4": "green", "g6": "red", "h5": "red"},
            },
            {
                "type": "move",
                "fen": ALEJADO_REAL,
                "orientation": "white",
                "title": "Créalo",
                "text": "En esta partida real aún no hay pasado alejado. Créalo con un cambio. (Lichess, puzzle 0NwPP)",
                "line": ["cxb5", "axb5", "a5"],
                "hint": "Cambia en b5 y empuja el peón de a.",
                "success": "Exacto: después de cxb5 axb5 a5, tu peón de a ya no tiene a nadie delante. axb5 habría sido tablas.",
            },
            {
                "type": "play",
                "fen": ALEJADO,
                "orientation": "white",
                "title": "Juégalo",
                "text": "Usa el peón de a para alejar al rey negro y gana en el otro flanco.",
                "goal": "win",
                "moves": 40,
                "hint": "Empuja el peón de a para que el rey negro tenga que ir a por él, y lleva tu rey a g6 y h5.",
                "success": "El rey negro se fue a por el peón de a y tu rey se quedó con todo lo demás.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de peones de partidas reales, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-caballo-peon",
        "course": "finales",
        "title": "Caballo contra peón",
        "summary": "El caballo no es rápido, pero sabe ponerse delante del peón.",
        "minutes": 8,
        "theme": "knightEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": CAB_PEON,
                "orientation": "white",
                "title": "Controla las casillas de delante",
                "text": (
                    "El peón negro quiere ir a b2 y b1. Tu rey está demasiado lejos, así que todo depende del caballo: "
                    "tiene que vigilar las casillas por las que pasará el peón, no perseguirlo."
                ),
                "arrows": [["b3", "b1", "red"]],
                "squares": {"b2": "red", "b1": "red", "c1": "yellow"},
            },
            {
                "type": "select",
                "fen": CAB_PEON,
                "orientation": "white",
                "title": "La casilla clave",
                "text": "¿A qué casilla saltas con el caballo de e1? Púlsala.",
                "answer": "d3",
                "wrong": {
                    "f3": "Desde f3 todavía aguantas, pero desde d3 el caballo vigila b2 y c1 a la vez: es la casilla ideal.",
                    "c2": "En c2 el peón de b3 se come el caballo.",
                    "g2": "Desde g2 el caballo se aleja: el peón llega a b1.",
                },
                "success": "Exacto: desde d3 el caballo controla b2 y c1. El peón ya no puede avanzar sin que lo captures.",
            },
            {
                "type": "play",
                "fen": CAB_PEON,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Detén el peón con el caballo hasta que llegue tu rey.",
                "goal": "draw",
                "moves": 15,
                "hint": "Lleva el caballo a d3 y no lo apartes de b2 ni de b1.",
                "success": "El caballo frenó el peón desde lejos.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de caballo de partidas reales, de tu nivel.",
                "theme": "knightEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-caballo",
        "course": "finales",
        "title": "Finales de caballo",
        "summary": "Se parecen a los de peones: un peón de más suele ganar, y el caballo odia los peones de torre.",
        "minutes": 9,
        "theme": "knightEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": CAB_REAL,
                "orientation": "white",
                "title": "Desviar al caballo",
                "text": (
                    "El caballo negro de c7 es lo único que frena tu peón de a7. Un caballo tiene que estar muy cerca "
                    "para parar un peón: si lo obligas a irse, el peón corona. (Lichess, puzzle Ck6yo)"
                ),
                "arrows": [["c7", "a8", "red"], ["d6", "b5", "green"]],
                "squares": {"a8": "yellow", "c7": "red"},
            },
            {
                "type": "move",
                "fen": CAB_REAL,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Desvía al caballo negro y corona.",
                "line": ["Nb5+", "Nxb5", "a8=Q"],
                "hint": "Ofrece tu caballo en b5 con jaque.",
                "success": "¡Dama! Cb5+ obligó al caballo negro a capturar y dejar libre a8.",
            },
            {
                "type": "play",
                "fen": CAB_GANA,
                "orientation": "white",
                "title": "Rey, caballo y peón",
                "text": "Con un peón de más y el rey rival solo, gana: corona sin perder el peón.",
                "goal": "win",
                "moves": 30,
                "hint": "El rey delante del peón, y el caballo a protegerlo o a quitarle casillas al rey negro.",
                "success": "Bien llevado: el peón coronó escoltado.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de caballo de partidas reales, de tu nivel.",
                "theme": "knightEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-color-equivocado",
        "course": "finales",
        "title": "El alfil del color equivocado",
        "summary": "Alfil y peón de torre no siempre ganan: si el alfil no controla la casilla de coronación, son tablas.",
        "minutes": 8,
        "theme": "bishopEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": COLOR_EQ,
                "orientation": "black",
                "title": "Una esquina inexpugnable",
                "text": (
                    "Las blancas tienen alfil y peón de más, pero el peón es de torre y corona en h8, una casilla oscura. "
                    "Su alfil es de claras: nunca podrá echar a tu rey de h8. Si llegas a la esquina, son tablas."
                ),
                "arrows": [["f7", "h8", "green"]],
                "squares": {"h8": "green", "c4": "red"},
            },
            {
                "type": "choice",
                "fen": COLOR_OK,
                "orientation": "black",
                "title": "¿Y con este alfil?",
                "text": "Ahora el alfil blanco está en d4. ¿Puedes salvarte igual yendo a h8?",
                "options": [
                    {"text": "No: este alfil sí controla h8", "correct": True,
                     "why": "Eso es. El alfil de d4 es de casillas oscuras, como h8: echa a tu rey de la esquina y el peón corona. Stockfish ve mate."},
                    {"text": "Sí, la esquina siempre salva", "correct": False,
                     "why": "Solo si el alfil no puede controlar la casilla de coronación. Aquí sí puede."},
                ],
            },
            {
                "type": "play",
                "fen": COLOR_EQ,
                "orientation": "black",
                "title": "Corre a la esquina",
                "text": "Juegas con negras. Llega a la esquina y aguanta.",
                "goal": "draw",
                "moves": 20,
                "hint": "Directo hacia g8 y h8. Cuidado con …Re7: te alejas de la esquina y pierdes.",
                "success": "El alfil equivocado no puede echarte de h8: ni el rey blanco ni el peón pueden con eso sin ahogarte.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de alfil de partidas reales, de tu nivel.",
                "theme": "bishopEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-alfiles-opuestos",
        "course": "finales",
        "title": "Alfiles de distinto color",
        "summary": "Con alfiles de distinto color, hasta dos peones de menos pueden ser tablas.",
        "minutes": 8,
        "theme": "bishopEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": OPUESTOS,
                "orientation": "black",
                "title": "Cada uno en su color",
                "text": (
                    "Las blancas tienen dos peones de más. Pero tu alfil va por casillas oscuras y el suyo por claras: "
                    "el blanco nunca podrá echar a tu alfil. Tu alfil, en d6, bloquea el peón de d5, y tu rey, en e7, "
                    "vigila e6 y f6: ningún peón puede avanzar."
                ),
                "arrows": [["d6", "f4", "green"]],
                "squares": {"e7": "green", "d6": "green", "e6": "yellow", "f6": "yellow"},
            },
            {
                "type": "choice",
                "fen": OPUESTOS,
                "orientation": "black",
                "title": "¿Por qué aguanta?",
                "text": "¿Qué hace que esta posición sea de tablas con dos peones de menos?",
                "options": [
                    {"text": "Bloqueas en casillas que el alfil rival no puede atacar", "correct": True,
                     "why": "Eso es. El alfil blanco es de claras y tus piezas están en oscuras: nadie puede echarlas. Stockfish: tablas."},
                    {"text": "Los peones blancos están doblados", "correct": False,
                     "why": "Están en d5 y f5: no están doblados."},
                    {"text": "Tu rey está más cerca", "correct": False,
                     "why": "Los reyes están igual de cerca. La clave es el color de las casillas."},
                ],
            },
            {
                "type": "play",
                "fen": OPUESTOS,
                "orientation": "black",
                "title": "Aguanta",
                "text": "Juegas con negras y mueven primero las blancas. Mantén el bloqueo.",
                "goal": "draw",
                "moves": 25,
                "color": "black",
                "hint": "No cambies el alfil por un peón si no hace falta: tu alfil debe vigilar las casillas oscuras delante de los peones.",
                "success": "Tablas con dos peones de menos: la magia de los alfiles de distinto color.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de alfil de partidas reales, de tu nivel.",
                "theme": "bishopEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-corte-rey",
        "course": "finales",
        "title": "Cortar al rey con la torre",
        "summary": "Una torre en una columna puede dejar al rey rival fuera de juego.",
        "minutes": 9,
        "theme": "rookEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": CORTE,
                "orientation": "white",
                "title": "Una pared",
                "text": (
                    "Tu torre de d1 corta al rey negro: no puede cruzar la columna d para ayudar contra tu peón de e4. "
                    "Con el rey rival cortado, tu rey escolta el peón y gana. Lo que no puedes hacer es soltar la pared."
                ),
                "arrows": [["d1", "d8", "green"]],
                "squares": {"c4": "red", "e4": "blue"},
            },
            {
                "type": "choice",
                "fen": CORTE,
                "orientation": "white",
                "title": "¿Qué juegas?",
                "text": "¿Cuál es la jugada correcta?",
                "options": [
                    {"text": "Re3: el rey sube junto al peón", "correct": True,
                     "why": "Eso es. La torre sigue cortando y tu rey escolta el peón. Stockfish: ganando."},
                    {"text": "e5: el peón corre", "correct": False,
                     "why": "Sin el rey al lado, …Te8 y el peón cae. Stockfish: tablas."},
                    {"text": "Tc1+: jaque", "correct": False,
                     "why": "Un jaque sin sentido: el rey negro va a d4, cruza la columna y llega a tu peón. Tablas."},
                ],
            },
            {
                "type": "choice",
                "fen": CORTE_PEON,
                "orientation": "white",
                "title": "Torre contra peón",
                "text": "Ahora es tu torre contra un peón negro. ¿Qué jugada gana?",
                "options": [
                    {"text": "Td1: plantarse delante del peón", "correct": True,
                     "why": "Eso es: la torre controla toda la columna por la que tiene que pasar el peón, y tu rey llega a tiempo. Stockfish: ganando."},
                    {"text": "Te1: cortar al rey por la columna e", "correct": False,
                     "why": "…d3 y el peón corre antes de que tu torre o tu rey lleguen a pararlo. Stockfish: tablas."},
                    {"text": "Tb4: atacar el peón", "correct": False,
                     "why": "…d3: el peón se escapa de tu torre y el rey negro lo acompaña. Stockfish: tablas."},
                ],
            },
            {
                "type": "play",
                "fen": CORTE_JUGAR,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Gana el peón: corta al rey negro con la torre y acerca el tuyo.",
                "goal": "win",
                "moves": 15,
                "hint": "Primero deja al rey negro lejos del peón con la torre; luego tu rey se acerca a por él.",
                "success": "Pared con la torre, rey que se acerca y peón capturado: la técnica básica de torre contra peón.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de torre de partidas reales, de tu nivel.",
                "theme": "rookEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-torre-detras",
        "course": "finales",
        "title": "La torre, detrás del peón pasado",
        "summary": "La regla de Tarrasch: las torres van detrás de los peones pasados, los tuyos y los del rival.",
        "minutes": 9,
        "theme": "rookEndgame",
        "steps": [
            {
                "type": "choice",
                "fen": DETRAS,
                "orientation": "white",
                "title": "¿Detrás o delante?",
                "text": (
                    "Tienes un peón pasado en a6. Aquí tu torre está detrás (a1) y la negra delante (a8). "
                    "Si fuera al revés (tu torre en a8 y la negra en a1), ¿qué te gustaría más?"
                ),
                "arrows": [["a1", "a6", "green"]],
                "options": [
                    {"text": "Así: mi torre detrás del peón", "correct": True,
                     "why": "Eso es. Tu torre empuja el peón y cada avance le da más espacio; la negra queda atada a a8. Stockfish: +5."},
                    {"text": "Al revés: mi torre delante", "correct": False,
                     "why": "Con la torre delante, el peón no puede avanzar y tu torre queda presa. Stockfish lo ve casi tablas (+0,5)."},
                ],
            },
            {
                "type": "explain",
                "fen": DELANTE,
                "orientation": "white",
                "title": "La torre presa",
                "text": (
                    "Esta es la versión mala: tu torre está en a8, delante del peón, y no puede moverse sin dejarlo caer. "
                    "La torre negra, detrás, ataca el peón y además puede dar jaques. Así son tablas."
                ),
                "arrows": [["a1", "a7", "red"]],
                "squares": {"a8": "red", "a7": "yellow"},
            },
            {
                "type": "choice",
                "fen": DETRAS_RIVAL,
                "orientation": "white",
                "title": "Contra el peón rival",
                "text": "La regla vale también para frenar un pasado del rival. Tu torre está detrás del peón de c3. ¿Qué juegas?",
                "options": [
                    {"text": "Td8+: jaque, y el rey negro se aleja del peón", "correct": True,
                     "why": "Exacto. El rey negro tiene que apartarse del peón, tu rey se acerca a por él y la torre vuelve a vigilarlo. Stockfish: ganas."},
                    {"text": "Tf8: esperar", "correct": False,
                     "why": "…c2 y el peón corona apoyado por el rey. Stockfish: tablas como mucho."},
                ],
            },
            {
                "type": "play",
                "fen": DETRAS_RIVAL,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Detén el peón desde detrás y gánalo.",
                "goal": "win",
                "moves": 20,
                "hint": "Jaque en d8 para alejar al rey negro; luego tu rey se acerca al peón.",
                "success": "Peón capturado. Con la torre detrás, el peón nunca escapa de su vista.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de torre de partidas reales, de tu nivel.",
                "theme": "rookEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-torre-activa",
        "course": "finales",
        "title": "Torre activa, torre pasiva",
        "summary": "En los finales de torres, una torre activa vale casi un peón.",
        "minutes": 8,
        "theme": "rookEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": ACTIVA,
                "orientation": "black",
                "title": "Un peón de menos… y tablas",
                "text": (
                    "Juegas con negras y tienes un peón de menos. Pero tu torre está activa: desde a2 vigila el peón de a4 "
                    "por detrás y ataca f2. La torre blanca, delante de su peón, apenas puede moverse."
                ),
                "arrows": [["a2", "a4", "green"], ["a2", "f2", "green"]],
                "squares": {"a5": "red"},
            },
            {
                "type": "choice",
                "fen": ACTIVA,
                "orientation": "black",
                "title": "La tentación",
                "text": "Imagina que pudieras llevar tu torre a a8, para bloquear el peón desde delante. ¿Sería buena idea?",
                "options": [
                    {"text": "No: allí la torre queda pasiva", "correct": True,
                     "why": "Eso es. En a8 tu torre solo bloquea, y la blanca, ya detrás del peón, quedaría libre. Una torre pasiva pierde; una activa empata."},
                    {"text": "Sí: así el peón no avanza", "correct": False,
                     "why": "El peón no avanza, pero tu torre no hace nada más, y la blanca queda libre para atacar tus peones."},
                ],
            },
            {
                "type": "play",
                "fen": ACTIVA,
                "orientation": "black",
                "title": "Aguanta con la torre activa",
                "text": "Mueven las blancas. Mantén tu torre activa y haz tablas.",
                "goal": "draw",
                "moves": 20,
                "color": "black",
                "hint": "Tu torre se queda detrás del peón de a o ataca peones; el rey, cerca de sus peones.",
                "success": "Tablas con un peón de menos. Actividad antes que material.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de torre de partidas reales, de tu nivel.",
                "theme": "rookEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-vancura",
        "course": "finales",
        "title": "La posición de Vancura",
        "summary": "La defensa lateral contra el peón de torre: tablas aunque el peón esté en sexta.",
        "minutes": 8,
        "theme": "rookEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": VANCURA,
                "orientation": "black",
                "title": "Desde el costado",
                "text": (
                    "El peón blanco de a6 tiene su torre delante, en a8. Tu torre ataca el peón por el costado, desde f6: "
                    "la torre blanca no puede apartarse sin dejarlo caer, y si el rey blanco viene a ayudar, lo echas a jaques "
                    "desde atrás. Tu rey, tranquilo en g7."
                ),
                "arrows": [["f6", "a6", "green"]],
                "squares": {"g7": "green", "a8": "red"},
            },
            {
                "type": "choice",
                "fen": VANCURA,
                "orientation": "black",
                "title": "Tu rey",
                "text": "¿Dónde quieres tener tu rey en esta defensa?",
                "options": [
                    {"text": "En g7 o h7, lejos de los jaques", "correct": True,
                     "why": "Eso es. Ahí la torre blanca no puede dar jaques útiles y, si a7, la torre se pone detrás del peón."},
                    {"text": "Corriendo hacia el peón", "correct": False,
                     "why": "Tu rey se metería en la columna y la torre blanca lo cazaría con jaques o ganaría tiempo. El trabajo lo hace la torre."},
                ],
            },
            {
                "type": "play",
                "fen": VANCURA,
                "orientation": "black",
                "title": "Ahora tú",
                "text": "Defiende la posición de Vancura y haz tablas.",
                "goal": "draw",
                "moves": 20,
                "hint": "La torre ataca el peón desde la sexta fila; si el rey blanco se acerca, jaques desde atrás.",
                "success": "La defensa lateral de Vancura. Una de las posiciones más útiles de los finales de torres.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de torre de partidas reales, de tu nivel.",
                "theme": "rookEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-torre-alfil",
        "course": "finales",
        "title": "Torre contra alfil",
        "summary": "Una torre contra un alfil suele ser tablas… si el rey sabe a qué esquina ir.",
        "minutes": 8,
        "theme": "rookEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": TORRE_ALFIL,
                "orientation": "black",
                "title": "La esquina buena",
                "text": (
                    "Torre contra alfil, sin peones. Tu alfil es de casillas claras y tu rey está en h8, una esquina oscura: "
                    "la esquina buena. Si la torre da jaque en la octava, el alfil tapa en g8, y el rey blanco no puede "
                    "acercarse sin ahogarte."
                ),
                "squares": {"h8": "green", "g8": "green"},
            },
            {
                "type": "choice",
                "fen": TORRE_ALFIL,
                "orientation": "black",
                "title": "Elige esquina",
                "text": "Con un alfil de casillas claras, ¿a qué esquina debe ir tu rey?",
                "options": [
                    {"text": "A una oscura, de distinto color que el alfil", "correct": True,
                     "why": "Eso es. Así el alfil puede tapar los jaques en la casilla de al lado, que es clara."},
                    {"text": "A una clara, del color del alfil", "correct": False,
                     "why": "En la esquina de su color, el alfil no puede tapar en la casilla de al lado y llegan los mates."},
                ],
            },
            {
                "type": "play",
                "fen": TORRE_ALFIL,
                "orientation": "black",
                "title": "Aguanta",
                "text": "Defiende con el rey en la esquina buena y haz tablas.",
                "goal": "draw",
                "moves": 20,
                "hint": "Tu rey entre g8 y h8; el alfil tapa en g8 cuando haga falta. No lo dejes donde lo pueda atrapar la torre.",
                "success": "Rey en la esquina buena y alfil tapando. La torre no puede con eso.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de torre de partidas reales, de tu nivel.",
                "theme": "rookEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-dama-peon-tablas",
        "course": "finales",
        "title": "Dama contra peón: las tablas",
        "summary": "La dama casi siempre gana a un peón en séptima… salvo si es de alfil o de torre.",
        "minutes": 8,
        "theme": "queenEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": DAMA_ALFIL,
                "orientation": "black",
                "title": "El truco del ahogado",
                "text": (
                    "Contra un peón central, la dama da jaques hasta obligar al rey a ponerse delante del peón y así gana "
                    "tiempos para acercar su rey. Con un peón de alfil no funciona: el rey negro se va a la esquina a1 y, "
                    "si la dama se come el peón, es ahogado."
                ),
                "arrows": [["b2", "a1", "green"]],
                "squares": {"a1": "green", "c2": "yellow"},
            },
            {
                "type": "choice",
                "fen": DAMA_CENTRAL,
                "orientation": "black",
                "title": "¿Y este peón?",
                "text": "Ahora el peón está en d2. ¿Pueden salvarse las negras igual?",
                "options": [
                    {"text": "No: con un peón central la dama gana", "correct": True,
                     "why": "Eso es. No hay esquina cerca para el truco del ahogado: la dama gana tiempos con jaques y llega su rey. Stockfish ve mate."},
                    {"text": "Sí: cualquier peón en séptima hace tablas", "correct": False,
                     "why": "Solo los peones de alfil y de torre, y con el rey rival lejos."},
                ],
            },
            {
                "type": "explain",
                "fen": DAMA_TORRE,
                "orientation": "black",
                "title": "Con el peón de torre",
                "text": (
                    "Con el peón de torre es aún más fácil: tu rey se mete en a1, delante del peón, y si la dama le quita "
                    "todas las casillas, es ahogado. El rey blanco está demasiado lejos para ayudar."
                ),
                "squares": {"a1": "green", "a2": "yellow"},
            },
            {
                "type": "play",
                "fen": DAMA_ALFIL,
                "orientation": "black",
                "title": "Ahora tú",
                "text": "Juegas con negras y mueve primero la dama. Haz tablas con el truco del ahogado.",
                "goal": "draw",
                "moves": 20,
                "color": "black",
                "hint": "Mantén el peón en c2 y, cuando haga falta, mete el rey en a1: si la dama come en c2, es ahogado.",
                "success": "Tablas con un peón contra una dama. Recuerda: peón de alfil o de torre en séptima y el rey rival lejos.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de finales de dama de partidas reales, de tu nivel.",
                "theme": "queenEndgame",
                "count": 5,
            },
        ],
    },
]
