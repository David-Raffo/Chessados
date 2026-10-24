"""Curso «Finales» (mates básicos y finales de rey y peón, torre y dama). Formato: ver app/learn.py.

Cada lección enseña la técnica con ejemplos jugada a jugada y termina jugando la posición contra
Stockfish (las mismas posiciones de app/lessons.py). Las líneas y las respuestas de los choice se
comprobaron con Stockfish; la evaluación está en el comentario de cada posición.
"""

# --- Mates básicos ---------------------------------------------------------------------
# Mate con dos torres (mate en 5): Th5 Re6 Ta6+ Rf7 Th7+ Rg8 Tb7 Rf8 Ta8#.
DOS_TORRES = "8/8/3k4/8/8/8/8/R3K2R w - - 0 1"
# El rey ataca la torre de h7: Tb7 (mate en 2) frente a Ta8+?? Rxh7.
TORRES_ATAQUE = "6k1/7R/R7/8/8/8/8/4K3 w - - 6 4"
# Ta8# es el único mate.
TORRES_MATE = "5k2/1R6/R7/8/8/8/8/4K3 w - - 8 5"
# Mate de dama (mate en 11).
DAMA = "8/8/8/4k3/8/8/8/3QK3 w - - 0 1"
# Dg7# es el único mate; Df7?? es ahogado y Dc8+ deja escapar al rey por h7.
DAMA_MATE = "7k/2Q5/5K2/8/8/8/8/8 w - - 0 1"
# Mate de torre.
TORRE = "8/8/8/4k3/8/8/8/4K2R w - - 0 1"
# La torre de e1 encierra al rey en las columnas a-d.
TORRE_CAJA = "8/8/8/3k4/8/8/8/4R1K1 w - - 0 1"
# Reyes enfrentados y el rival en el borde: Ta8#.
TORRE_MATE = "4k3/8/4K3/8/8/8/8/R7 w - - 0 1"
# Reyes sin enfrentar: Ta8+ no es mate, el rey escapa a c7.
TORRE_NO_MATE = "3k4/8/4K3/8/8/8/8/R7 w - - 0 1"
# Mate con dos alfiles.
DOS_ALFILES = "8/8/8/4k3/8/8/8/2B1KB2 w - - 0 1"
# Rey en la esquina: mate en 5 (Ad5 Rh7 Ac4 Rh8 Rf7 Rh7 Ad3+ Rh8 Ae5#).
ALFILES_ESQUINA = "7k/8/5K2/8/4BB2/8/8/8 w - - 0 1"
# Ae5# es el único mate.
ALFILES_MATE = "7k/5B2/6K1/8/5B2/8/8/8 w - - 0 1"
# Mate de alfil y caballo.
ALFIL_CABALLO = "8/8/8/4k3/8/8/8/1N2KB2 w - - 0 1"
# El mismo material con el rey negro cerca de la esquina buena (a8, clara como el alfil).
AC_ESQUINA = "8/3k4/8/8/8/8/8/1N2KB2 w - - 0 1"
# Mate en 3: Aa6 Ra8 Ab7+ Rb8 Ca6#.
AC_FINAL = "1k6/8/1K6/2N5/8/3B4/8/8 w - - 0 1"
# Ad5# es el único mate.
AC_MATE = "k7/3N4/1K2B3/8/8/8/8/8 w - - 0 1"

# --- Rey y peón ------------------------------------------------------------------------
# La regla del cuadrado: mueven las negras y alcanzan el peón (tablas).
CUADRADO = "8/8/8/4k3/P7/8/8/7K b - - 0 1"
# Rey en f6: si mueven las negras entra en el cuadrado (0,00)…
CUADRADO_NEGRAS = "8/8/5k2/8/P7/8/8/7K b - - 0 1"
# …pero si mueven las blancas, a5 encoge el cuadrado y el peón corona (+6,5).
CUADRADO_BLANCAS = "8/8/5k2/8/P7/8/8/7K w - - 0 1"
# Rey en sexta delante del peón: gana mueva quien mueva (+6,7 / +7,0).
REY_DELANTE = "4k3/8/4K3/4P3/8/8/8/8 w - - 0 1"
# Tras 1.Rd6 Rd8 2.e6 Re8 3.e7 Rf7: 4.Rd7! (mate en 8); 4.e8=D+?? Rxe8 tablas.
NO_CORONES = "8/4Pk2/3K4/8/8/8/8/8 w - - 0 1"
# La oposición: mueven las negras y las blancas ganan.
OPOSICION = "8/8/8/4k3/8/4K3/4P3/8 b - - 0 1"
# Toma la oposición: Re4 (+7,3); cualquier otra jugada, tablas.
OPOSICION_TOMA = "8/8/4k3/8/3K4/8/4P3/8 w - - 0 1"
# Sin la oposición pero con el peón atrás: 1.e3 devuelve el turno (+78).
OPOSICION_RESERVA = "8/8/4k3/8/4K3/8/4P3/8 w - - 0 1"
# Defender: mueven las blancas y las negras hacen tablas.
DEFENSA = "8/8/8/4k3/8/4K3/4P3/8 w - - 0 1"
# Tras 1.Rd3: solo 1…Rd5 hace tablas (las demás, +8,9).
DEFENSA_RD3 = "8/8/8/4k3/8/3K4/4P3/8 b - - 0 1"
# Bloquear el peón: las negras hacen tablas retrocediendo delante del peón.
BLOQUEO = "4k3/8/8/4K3/4P3/8/8/8 b - - 0 1"
# Re8 (tablas) frente a Rf8 o Rf6 (pierden).
BLOQUEO_ELIGE = "8/4k3/4P3/3K4/8/8/8/8 b - - 0 4"
# Jaque en séptima: Re8 (tablas) frente a Rc8?? (mate en 3).
BLOQUEO_SEPTIMA = "3k4/4P3/3K4/8/8/8/8/8 b - - 0 1"
# Peón de torre: el rey negro llega a la esquina y son tablas.
PEON_TORRE = "7k/8/8/6KP/8/8/8/8 b - - 0 1"
# El ahogado de la esquina.
PEON_TORRE_AHOGADO = "7k/7P/6K1/8/8/8/8/8 b - - 0 1"

# --- Torres y damas ----------------------------------------------------------------------
# Lucena: las blancas ganan construyendo el puente (+4,3; la línea del puente acaba en mate en 15).
LUCENA = "1K6/1P1k4/8/8/8/8/r7/2R5 w - - 0 1"
# Philidor: las negras hacen tablas. Tb6 (0,00) frente a Th1?? (Txh1) o Th8? (Ta8+ y Txh8).
PHILIDOR = "4k3/8/7r/4K3/4P3/8/8/R7 b - - 0 1"
# Philidor clásico: tras e6, la torre baja a la primera fila y da jaques por detrás (0,00).
PHILIDOR_CLASICO = "4k3/R7/1r6/3KP3/8/8/8/8 w - - 0 1"
# Dama contra peón de d en séptima: ganan las blancas.
DAMA_PEON = "Q7/8/8/8/8/8/3pk3/7K w - - 0 1"

LESSONS = [
    {
        "id": "final-dos-torres",
        "course": "finales",
        "title": "Mate con dos torres",
        "summary": "La escalera: una torre corta una fila, la otra da jaque en la siguiente, y el rey sube hasta el borde.",
        "minutes": 8,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": DOS_TORRES,
                "orientation": "white",
                "title": "La escalera",
                "text": (
                    "Con dos torres no necesitas ni a tu rey. Una torre corta una fila para que el rey no baje; la otra "
                    "da jaque en la fila de al lado y lo obliga a subir. Luego se cambian los papeles. Escalón a escalón."
                ),
                "moves": [
                    {"san": "Rh5", "text": "La torre de h5 corta la quinta fila: el rey negro ya no puede bajar."},
                    {"san": "Ke6", "text": "El rey busca acercarse a tus torres."},
                    {"san": "Ra6+", "text": "Jaque en la sexta: tiene que subir a la séptima."},
                    {"san": "Kf7", "text": "Sube… y se acerca a las torres."},
                    {"san": "Rh7+", "text": "Otro escalón: jaque en la séptima. Solo le queda la octava fila."},
                    {"san": "Kg8", "text": "¡El rey ataca a tu torre de h7!"},
                    {"san": "Rb7", "text": "La regla de oro: si el rey ataca una torre, llévala al otro extremo de la fila. La séptima sigue cerrada."},
                    {"san": "Kf8", "text": "No le queda nada mejor."},
                    {"san": "Ra8#", "text": "Mate: una torre en la séptima y la otra dando jaque en la octava."},
                ],
            },
            {
                "type": "choice",
                "fen": TORRES_ATAQUE,
                "orientation": "white",
                "title": "El rey ataca",
                "text": "El rey negro de g8 ataca tu torre de h7. ¿Qué haces?",
                "options": [
                    {"text": "Tb7: llevarla al otro extremo de la fila", "correct": True,
                     "why": "Exacto. La torre sigue cerrando la séptima, lejos del rey. Después, Ta8 es mate."},
                    {"text": "Ta8+: dar jaque con la otra torre", "correct": False,
                     "why": "¡Cuidado! …Rxh7 y te comen una torre. Con la otra todavía ganas, pero mucho más despacio."},
                ],
            },
            {
                "type": "move",
                "fen": TORRES_MATE,
                "orientation": "white",
                "title": "Remata",
                "text": "La escalera ha llegado arriba. Da mate.",
                "line": ["Ra8#"],
                "hint": "La torre de a6 sube a la octava fila.",
                "success": "Mate. La torre de b7 corta la séptima y la de a8 da jaque en la octava.",
            },
            {
                "type": "play",
                "fen": DOS_TORRES,
                "orientation": "white",
                "title": "Ahora contra Stockfish",
                "text": "Da mate con las dos torres. Stockfish defenderá a la perfección.",
                "goal": "mate",
                "moves": 20,
                "hint": "Una torre corta una fila y la otra da jaque en la siguiente. Si el rey ataca una torre, llévala al otro extremo.",
                "success": "Dominas la escalera: el mate más sencillo, y el que más partidas decide.",
            },
        ],
    },
    {
        "id": "final-dama",
        "course": "finales",
        "title": "Mate de dama",
        "summary": "La dama encoge la caja del rey y tu rey se acerca para el golpe final. Ojo con el ahogado.",
        "minutes": 9,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": DAMA,
                "orientation": "white",
                "title": "Encoge la caja",
                "text": (
                    "La dama sola no puede dar mate: necesita a su rey. La técnica: con la dama, encierra al rey rival en "
                    "una caja cada vez más pequeña (a menudo a salto de caballo de él) y, cuando esté en el borde, trae a "
                    "tu rey. Así lo hace Stockfish."
                ),
                "moves": [
                    {"san": "Qd3", "text": "La dama corta la columna d y la tercera fila."},
                    {"san": "Ke6", "text": "El rey negro se queda en el centro."},
                    {"san": "Ke2", "text": "Tu rey se pone en marcha. Sin él no hay mate."},
                    {"san": "Ke5", "text": "El rey negro espera."},
                    {"san": "Ke3", "text": "Tu rey sigue acercándose."},
                    {"san": "Kf6", "text": "Se aparta hacia el flanco de rey."},
                    {"san": "Qe4", "text": "La caja se encoge: ahora tampoco puede usar la columna e."},
                    {"san": "Kg5", "text": "Cada vez menos casillas."},
                    {"san": "Kf3", "text": "Tu rey le corta la retirada."},
                    {"san": "Kh5", "text": "Ya está pegado al borde."},
                    {"san": "Kf4", "text": "Tu rey se acerca más."},
                    {"san": "Kh6", "text": "El rey negro no tiene adónde ir."},
                    {"san": "Qe8", "text": "La dama le quita la octava fila."},
                    {"san": "Kg7", "text": "Sube lo que puede."},
                    {"san": "Kg5", "text": "Tu rey, delante del suyo."},
                    {"san": "Kh7", "text": "El rey negro ya está en la esquina."},
                    {"san": "Qe7+", "text": "Jaque: solo le queda g8."},
                    {"san": "Kg8", "text": "Última casilla."},
                    {"san": "Kg6", "text": "Tu rey cubre g7, h7 y f7."},
                    {"san": "Kh8", "text": "No hay más."},
                    {"san": "Qg7#", "text": "Mate: la dama, protegida por tu rey, pegada al rey rival."},
                ],
            },
            {
                "type": "choice",
                "fen": DAMA_MATE,
                "orientation": "white",
                "title": "¿Mate o ahogado?",
                "text": "El rey negro está en h8 y no tiene movimientos de sobra. ¿Qué juegas?",
                "options": [
                    {"text": "Dg7#", "correct": True,
                     "why": "Mate: la dama da jaque pegada al rey y la protege tu rey de f6."},
                    {"text": "Df7", "correct": False,
                     "why": "¡Ahogado! El rey negro no está en jaque y no tiene ninguna casilla: tablas. El error más famoso de este final."},
                    {"text": "Dc8+", "correct": False,
                     "why": "Es jaque, pero el rey escapa a h7. No pasa nada grave, pero pierdes tiempo."},
                ],
            },
            {
                "type": "move",
                "fen": DAMA_MATE,
                "orientation": "white",
                "title": "Sin regalos",
                "text": "Da mate en una.",
                "line": ["Qg7#"],
                "hint": "La dama se pone pegada al rey, protegida por tu rey.",
                "success": "Mate. Regla práctica: cuando el rey rival tenga pocas casillas, comprueba siempre que le dejas al menos una o que es jaque.",
            },
            {
                "type": "play",
                "fen": DAMA,
                "orientation": "white",
                "title": "Ahora contra Stockfish",
                "text": "Da mate con dama y rey.",
                "goal": "mate",
                "moves": 25,
                "hint": "Encierra al rey con la dama (a salto de caballo), empújalo al borde y acerca tu rey. Cuidado con el ahogado.",
                "success": "¡Mate de dama! Con este final ya no se te escapará ninguna partida ganada.",
            },
        ],
    },
    {
        "id": "final-torre",
        "course": "finales",
        "title": "Mate de torre",
        "summary": "La torre encierra al rey en una caja; tu rey lo empuja y, con los reyes enfrentados, la torre da mate.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": TORRE_CAJA,
                "orientation": "white",
                "title": "La caja",
                "text": (
                    "La torre de e1 le prohíbe al rey cruzar la columna e: está encerrado en las columnas a-d. Esa es la "
                    "caja. Tu trabajo es hacerla cada vez más pequeña, acercando tu rey y moviendo la torre una columna "
                    "o una fila cuando el rey rival se aparte."
                ),
                "squares": {"e1": "green", "e2": "red", "e3": "red", "e4": "red", "e5": "red", "e6": "red", "e7": "red", "e8": "red"},
            },
            {
                "type": "explain",
                "fen": TORRE_MATE,
                "orientation": "white",
                "title": "El dibujo del mate",
                "text": (
                    "El mate llega cuando el rey rival está en el borde y tu rey se le pone enfrente, con una casilla en "
                    "medio. Tu rey le quita la fila de delante y la torre da jaque en el borde."
                ),
                "arrows": [["a1", "a8", "green"]],
                "squares": {"d7": "red", "e7": "red", "f7": "red"},
            },
            {
                "type": "move",
                "fen": TORRE_MATE,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Los reyes están enfrentados. Da mate.",
                "line": ["Ra8#"],
                "hint": "La torre sube a la octava fila.",
                "success": "Mate: tu rey cubre d7, e7 y f7, y la torre la octava fila.",
            },
            {
                "type": "choice",
                "fen": TORRE_NO_MATE,
                "orientation": "white",
                "title": "¿Y aquí?",
                "text": "El rey negro está en d8 y el tuyo en e6. ¿Es mate Ta8+?",
                "options": [
                    {"text": "Sí, es mate", "correct": False,
                     "why": "No: tu rey no está enfrente del suyo, y c7 queda libre."},
                    {"text": "No: el rey escapa a c7", "correct": True,
                     "why": "Eso es. Sin los reyes enfrentados, el rey rival tiene una salida. Primero colócate delante de él."},
                    {"text": "No: el rey se come la torre", "correct": False,
                     "why": "La torre de a8 está lejos del rey de d8: no puede comérsela."},
                ],
            },
            {
                "type": "play",
                "fen": TORRE,
                "orientation": "white",
                "title": "Ahora contra Stockfish",
                "text": "Da mate con rey y torre. Es el más largo de los mates básicos: paciencia.",
                "goal": "mate",
                "moves": 35,
                "hint": "Encierra al rey con la torre, acerca tu rey y, cuando los reyes se enfrenten con el rival en el borde, da jaque con la torre.",
                "success": "¡Mate de torre! El final básico más importante: aparece en muchísimas partidas.",
            },
        ],
    },
    {
        "id": "final-dos-alfiles",
        "course": "finales",
        "title": "Mate con dos alfiles",
        "summary": "Los dos alfiles juntos forman una muralla diagonal; empujan al rey a una esquina, cualquiera.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": ALFILES_ESQUINA,
                "orientation": "white",
                "title": "La muralla diagonal",
                "text": (
                    "Un alfil solo no da mate, pero dos alfiles uno al lado del otro cubren casillas de los dos colores y "
                    "forman una barrera que el rey no puede cruzar. Con el rey rival ya en la esquina, el final es así."
                ),
                "moves": [
                    {"san": "Bd5", "text": "El alfil claro le quita g8."},
                    {"san": "Kh7", "text": "El rey se mueve en su rincón."},
                    {"san": "Bc4", "text": "Una jugada de espera: el alfil sigue vigilando g8."},
                    {"san": "Kh8", "text": "Vuelve a la esquina."},
                    {"san": "Kf7", "text": "Tu rey le quita g7 y g8."},
                    {"san": "Kh7", "text": "Solo le quedan h7 y h8."},
                    {"san": "Bd3+", "text": "Jaque del alfil claro: vuelve a h8."},
                    {"san": "Kh8", "text": "Forzado."},
                    {"san": "Be5#", "text": "Mate: el alfil oscuro da jaque por la gran diagonal."},
                ],
            },
            {
                "type": "move",
                "fen": ALFILES_MATE,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "El rey está en la esquina. Da mate con el alfil de casillas oscuras.",
                "line": ["Be5#"],
                "hint": "El alfil de f4 busca la gran diagonal.",
                "success": "Mate: el alfil de f7 cubre g8, tu rey cubre g7 y h7, y el de e5 da jaque.",
            },
            {
                "type": "play",
                "fen": DOS_ALFILES,
                # Mate teórico sin peones: Stockfish, sin tablas de finales, lo valora en +2 o +3
                "min_eval": 150,
                "orientation": "white",
                "title": "Ahora contra Stockfish",
                "text": "Da mate con los dos alfiles.",
                "goal": "mate",
                "moves": 45,
                "hint": "Lleva los alfiles juntos, uno al lado del otro, y empuja al rey a cualquier esquina con la ayuda de tu rey.",
                "success": "¡Mate con dos alfiles! Ya sabes por qué la pareja de alfiles vale tanto.",
            },
        ],
    },
    {
        "id": "final-alfil-caballo",
        "course": "finales",
        "title": "Mate de alfil y caballo",
        "summary": "El más difícil de los mates básicos: solo se da en la esquina del color de tu alfil.",
        "minutes": 12,
        "theme": None,
        "steps": [
            {
                "type": "select",
                "fen": AC_ESQUINA,
                "orientation": "white",
                "title": "La esquina buena",
                "text": (
                    "Con alfil y caballo solo se puede dar mate en una esquina del mismo color que tu alfil. Tu alfil de f1 "
                    "va por casillas claras. Pulsa la esquina buena más cercana al rey negro."
                ),
                "answer": "a8",
                "wrong": {
                    "h8": "h8 es una casilla oscura: tu alfil nunca podría dar jaque allí.",
                    "a1": "a1 es oscura, y además está lejos del rey negro.",
                    "h1": "h1 también es clara, pero está en la otra punta: el rey negro está arriba.",
                },
                "success": "Exacto: a8 es clara, como tu alfil. Si el rey negro huye a una esquina oscura, tendrás que sacarlo de ahí.",
            },
            {
                "type": "explain",
                "fen": AC_FINAL,
                "orientation": "white",
                "title": "Los últimos pasos",
                "text": (
                    "Cuando el rey ya está junto a la esquina buena, los tres trabajan juntos: tu rey le quita la fila de "
                    "delante, el alfil da los jaques en las diagonales y el caballo tapa la última casilla."
                ),
                "moves": [
                    {"san": "Ba6", "text": "El alfil le quita b7 y c8."},
                    {"san": "Ka8", "text": "Se mete en la esquina."},
                    {"san": "Bb7+", "text": "Jaque del alfil: vuelve a b8."},
                    {"san": "Kb8", "text": "Forzado."},
                    {"san": "Na6#", "text": "Mate: el caballo da jaque y el alfil le quita a8."},
                ],
            },
            {
                "type": "move",
                "fen": AC_MATE,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "El rey está en a8. Da mate.",
                "line": ["Bd5#"],
                "hint": "El alfil busca la diagonal que llega a a8.",
                "success": "Mate: tu rey cubre a7 y b7, el caballo cubre b8 y el alfil da jaque desde d5.",
            },
            {
                "type": "play",
                "fen": ALFIL_CABALLO,
                # Mate teórico sin peones: Stockfish, sin tablas de finales, lo valora en +2 o +3
                "min_eval": 150,
                "orientation": "white",
                "title": "El reto",
                "text": "Da mate con alfil y caballo en 50 jugadas. Es difícil incluso para jugadores fuertes: si no sale, repítelo.",
                "goal": "mate",
                "moves": 50,
                "hint": "Empuja al rey al borde con tu rey y tus piezas, y llévalo hacia la esquina clara (a8 o h1). El caballo hace una ruta en forma de W.",
                "success": "¡Increíble! El mate de alfil y caballo es de los más difíciles: muy pocos aficionados lo saben dar.",
            },
        ],
    },
    {
        "id": "final-cuadrado",
        "course": "finales",
        "title": "La regla del cuadrado",
        "summary": "¿Alcanza tu rey al peón? Dibuja un cuadrado y lo sabrás sin calcular nada.",
        "minutes": 7,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": CUADRADO,
                "orientation": "black",
                "title": "Dibuja el cuadrado",
                "text": (
                    "Desde el peón de a4 hasta su casilla de coronación, a8, hay cinco casillas. Dibuja un cuadrado con "
                    "ese lado: de a4 a a8 y hasta la columna e. Si tu rey está dentro (o entra en su turno), alcanza el "
                    "peón. Tu rey de e5 está dentro."
                ),
                "squares": {"a4": "yellow", "a8": "yellow", "e8": "yellow", "e4": "yellow", "e5": "green"},
            },
            {
                "type": "choice",
                "fen": CUADRADO_NEGRAS,
                "orientation": "black",
                "title": "¿Llegas?",
                "text": "Tu rey está en f6, fuera del cuadrado. Te toca mover. ¿Alcanzas el peón?",
                "options": [
                    {"text": "Sí: con Re5 entro en el cuadrado", "correct": True,
                     "why": "Eso es. El cuadrado va de la columna a a la e: en una jugada estás dentro y el peón no se escapa."},
                    {"text": "No: estoy fuera del cuadrado", "correct": False,
                     "why": "Estás fuera, pero te toca a ti: en una jugada entras. Lo que cuenta es si entras en tu turno."},
                ],
            },
            {
                "type": "choice",
                "fen": CUADRADO_BLANCAS,
                "orientation": "black",
                "title": "¿Y si mueven ellas?",
                "text": "La misma posición, pero ahora mueven las blancas. ¿Alcanzas el peón?",
                "options": [
                    {"text": "No: a5 encoge el cuadrado", "correct": True,
                     "why": "Exacto. Con el peón en a5, el cuadrado va de a5 a d8: tu rey, en la columna e, ya no entra. Stockfish: el peón corona."},
                    {"text": "Sí, igual que antes", "correct": False,
                     "why": "El turno lo cambia todo: el peón avanza primero y el cuadrado se hace más pequeño."},
                ],
            },
            {
                "type": "play",
                "fen": CUADRADO,
                "orientation": "black",
                "color": "black",
                "title": "Ahora contra Stockfish",
                "text": "Juegas con negras. Alcanza el peón y consigue las tablas.",
                "goal": "draw",
                "moves": 12,
                "hint": "Lleva el rey en diagonal hacia el peón, sin salirte del cuadrado.",
                "success": "Con la regla del cuadrado sabrás al instante si un peón pasado corona o no.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con finales de peones, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-rey-delante",
        "course": "finales",
        "title": "El rey delante del peón",
        "summary": "Con tu rey en sexta delante de su peón, ganas siempre (salvo con el peón de torre).",
        "minutes": 8,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": REY_DELANTE,
                "orientation": "white",
                "title": "El rey abre camino",
                "text": (
                    "En los finales de rey y peón, el rey va delante: le abre paso al peón. Con tu rey en sexta delante "
                    "de tu peón, ganas mueva quien mueva. Así se hace."
                ),
                "moves": [
                    {"san": "Kd6", "text": "Tu rey sigue delante del peón y le quita casillas al rey negro."},
                    {"san": "Kd8", "text": "El rey negro intenta ponerse delante."},
                    {"san": "e6", "text": "Ahora sí avanza el peón: tu rey controla las casillas de su camino."},
                    {"san": "Ke8", "text": "El rey negro vuelve delante del peón."},
                    {"san": "e7", "text": "El peón llega a séptima…"},
                    {"san": "Kf7", "text": "…y el rey negro se aparta: no puede quedarse delante."},
                    {"san": "Kd7", "text": "Tu rey protege e8: el peón coronará en la jugada siguiente."},
                ],
            },
            {
                "type": "choice",
                "fen": "4k3/8/4K3/4P3/8/8/8/8 b - - 0 1",
                "orientation": "white",
                "title": "¿Y si mueven las negras?",
                "text": "La misma posición, pero ahora le toca al negro. ¿Ganan igual las blancas?",
                "options": [
                    {"text": "Sí: con el rey en sexta delante del peón, da igual quién mueva", "correct": True,
                     "why": "Eso es. Stockfish da a las blancas más de 6 peones de ventaja en los dos casos."},
                    {"text": "No: el negro tiene la oposición y hace tablas", "correct": False,
                     "why": "La oposición importa cuando tu rey está más atrás. Con el rey en sexta, delante del peón, ya no hay defensa."},
                ],
            },
            {
                "type": "move",
                "fen": NO_CORONES,
                "orientation": "white",
                "title": "No corones todavía",
                "text": "El peón está en e7 y el rey negro en f7. Corona con seguridad.",
                "line": ["Kd7"],
                "hint": "Si coronas ya, el rey negro se come la dama. Primero protege e8.",
                "success": "Exacto: primero Rd7 y el peón corona en la jugada siguiente. Con 1.e8=D+?? Rxe8 habrían sido tablas.",
            },
            {
                "type": "play",
                "fen": REY_DELANTE,
                "orientation": "white",
                "title": "Ahora contra Stockfish",
                "text": "Corona el peón y gana.",
                "goal": "win",
                "moves": 20,
                "hint": "Mantén tu rey delante del peón y avanza el peón solo cuando tu rey controle la casilla de delante.",
                "success": "Ganado: el rey abre camino y el peón le sigue.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con finales de peones, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-oposicion",
        "course": "finales",
        "title": "La oposición",
        "summary": "Reyes enfrentados con una casilla en medio: quien no tiene que mover, gana el pulso.",
        "minutes": 10,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": OPOSICION,
                "orientation": "white",
                "title": "Qué es la oposición",
                "text": (
                    "Los reyes están enfrentados en la columna e con una casilla en medio, y le toca al negro. Como los "
                    "reyes no pueden tocarse, el negro tiene que apartarse y dejar pasar a tu rey. Tienes la oposición."
                ),
                "squares": {"e3": "green", "e5": "red", "e4": "yellow"},
            },
            {
                "type": "explain",
                "fen": OPOSICION,
                "orientation": "white",
                "title": "Ganar terreno",
                "text": "Mira cómo tu rey va ganando terreno, tomando la oposición o rodeando al rey negro, hasta llegar a sexta.",
                "moves": [
                    {"san": "Kd6", "text": "El negro tiene que mover y cede."},
                    {"san": "Kd4", "text": "Oposición en la columna d: reyes enfrentados y le toca al negro."},
                    {"san": "Ke6", "text": "Vuelve a ceder."},
                    {"san": "Ke4", "text": "Otra vez la oposición."},
                    {"san": "Kf6", "text": "El negro se aparta hacia un lado…"},
                    {"san": "Kd5", "text": "…y tu rey avanza por el otro: lo rodea."},
                    {"san": "Ke7", "text": "El negro intenta frenarlo."},
                    {"san": "Ke5", "text": "Oposición de nuevo."},
                    {"san": "Kd7", "text": "Cede otra vez."},
                    {"san": "Kf6", "text": "Tu rey llega a sexta, delante del peón: la victoria ya es segura."},
                ],
            },
            {
                "type": "move",
                "fen": OPOSICION_TOMA,
                "orientation": "white",
                "title": "Toma la oposición",
                "text": "El rey negro está en e6. Coloca tu rey para tener la oposición.",
                "line": ["Ke4"],
                "hint": "Ponte enfrente del rey negro, con una casilla en medio.",
                "success": "Exacto: Re4. Cualquier otra jugada habría dejado tablas, según Stockfish.",
            },
            {
                "type": "choice",
                "fen": OPOSICION_RESERVA,
                "orientation": "white",
                "title": "Sin la oposición",
                "text": "Ahora los reyes están enfrentados, pero te toca a ti: la oposición la tiene el negro. ¿Está todo perdido?",
                "options": [
                    {"text": "No: e3 es una jugada de espera y le devuelve el turno al negro", "correct": True,
                     "why": "¡Eso es! El peón aún puede avanzar una casilla sin perder nada: es un tiempo de reserva. Stockfish: ganan las blancas."},
                    {"text": "Sí, ya solo son tablas", "correct": False,
                     "why": "Sería tablas si no tuvieras jugadas de espera. Pero tu peón puede ir a e3 y recuperar la oposición."},
                    {"text": "Hay que retroceder el rey", "correct": False,
                     "why": "Retroceder cede terreno: con Rf3 o Rd3 el negro iguala. La clave es la jugada de peón."},
                ],
            },
            {
                "type": "play",
                "fen": OPOSICION,
                "orientation": "white",
                "color": "white",
                "title": "Ahora contra Stockfish",
                "text": "Mueven las negras. Gana con la oposición y corona el peón.",
                "goal": "win",
                "moves": 25,
                "hint": "Mantén tu rey delante del peón y toma la oposición cada vez que el rey negro se enfrente al tuyo.",
                "success": "¡Ganado! La oposición es la herramienta más importante de los finales de peones.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con finales de peones, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-defensa-oposicion",
        "course": "finales",
        "title": "Defender con la oposición",
        "summary": "Si el rival tiene que mover, eres tú quien tiene la oposición: úsala para hacer tablas.",
        "minutes": 8,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": DEFENSA,
                "orientation": "black",
                "title": "Ahora defiendes tú",
                "text": (
                    "La misma posición de la lección anterior, pero le toca al blanco. Ahora la oposición es tuya: el rey "
                    "blanco tiene que apartarse. Si respondes bien a cada jugada, el peón nunca coronará."
                ),
                "squares": {"e5": "green", "e3": "red"},
            },
            {
                "type": "move",
                "fen": DEFENSA_RD3,
                "orientation": "black",
                "title": "Responde",
                "text": "El rey blanco se ha ido a d3. Mantén la oposición.",
                "line": ["Kd5"],
                "min_eval": -50,
                "hint": "Ponte enfrente del rey blanco, con una casilla en medio.",
                "success": "Exacto: Rd5. Cualquier otra jugada pierde, según Stockfish.",
            },
            {
                "type": "explain",
                "fen": DEFENSA,
                "orientation": "black",
                "title": "La defensa completa",
                "text": "Así se mantienen las tablas: delante del peón y enfrente del rey blanco.",
                "moves": [
                    {"san": "Kd3", "text": "El blanco intenta rodearte."},
                    {"san": "Kd5", "text": "Oposición."},
                    {"san": "e4+", "text": "El peón avanza con jaque."},
                    {"san": "Ke5", "text": "Te quedas delante del peón."},
                    {"san": "Ke3", "text": "El rey blanco se coloca detrás."},
                    {"san": "Ke6", "text": "¡Retrocede en línea recta! Así podrás tomar la oposición cuando avance."},
                    {"san": "Kd4", "text": "El rey blanco avanza."},
                    {"san": "Kd6", "text": "Oposición otra vez: no pasa."},
                ],
            },
            {
                "type": "play",
                "fen": DEFENSA,
                "orientation": "black",
                "color": "black",
                "title": "Ahora contra Stockfish",
                "text": "Juegas con negras y mueve Stockfish. Haz tablas.",
                "goal": "draw",
                "moves": 20,
                "hint": "Quédate delante del peón y responde a cada jugada del rey blanco enfrentándolo.",
                "success": "Defender bien un final de peones salva muchas partidas.",
            },
        ],
    },
    {
        "id": "final-bloquear-peon",
        "course": "finales",
        "title": "Bloquear el peón",
        "summary": "Retrocede en línea recta delante del peón y la partida acabará en ahogado.",
        "minutes": 8,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": BLOQUEO,
                "orientation": "black",
                "title": "La defensa perfecta",
                "text": (
                    "Tu rey está delante del peón. Retrocede en línea recta, siempre delante de él, y en el momento justo "
                    "ponte enfrente. Al final, el blanco solo podrá ahogarte."
                ),
                "moves": [
                    {"san": "Ke7", "text": "Retrocedes en línea recta."},
                    {"san": "Kd5", "text": "El rey blanco avanza."},
                    {"san": "Kd7", "text": "Le haces frente: oposición."},
                    {"san": "e5", "text": "El peón avanza."},
                    {"san": "Ke7", "text": "Te pones delante del peón."},
                    {"san": "e6", "text": "Otro paso."},
                    {"san": "Ke8", "text": "¡Atrás, en línea recta! Es la única jugada que hace tablas."},
                    {"san": "Kd6", "text": "El rey blanco llega a sexta."},
                    {"san": "Kd8", "text": "Oposición."},
                    {"san": "e7+", "text": "Jaque del peón."},
                    {"san": "Ke8", "text": "A la casilla de delante del peón."},
                    {"san": "Ke6", "text": "Si el blanco protege el peón… ¡ahogado! Tablas."},
                ],
            },
            {
                "type": "choice",
                "fen": BLOQUEO_ELIGE,
                "orientation": "black",
                "title": "El momento clave",
                "text": "El peón acaba de llegar a e6. ¿Dónde pones tu rey?",
                "options": [
                    {"text": "Re8: atrás, en línea recta", "correct": True,
                     "why": "Eso es. Desde e8 podrás hacer frente al rey blanco cuando llegue a sexta. Stockfish: tablas."},
                    {"text": "Rf8", "correct": False,
                     "why": "Te apartas de la columna del peón: Rd6, e7 y el peón corona. Stockfish: mate en 11."},
                    {"text": "Rf6", "correct": False,
                     "why": "Atacar el peón no sirve: Rd6 lo protege y corona. Stockfish: perdido."},
                ],
            },
            {
                "type": "move",
                "fen": BLOQUEO_SEPTIMA,
                "orientation": "black",
                "title": "El jaque en séptima",
                "text": "El peón te da jaque desde e7. ¿Adónde va tu rey?",
                "line": ["Ke8"],
                "min_eval": -50,
                "hint": "Ve a la casilla que está delante del peón.",
                "success": "¡Tablas! Delante del peón. Si el rey blanco lo protege desde e6, es ahogado. Con Rc8?? habría sido mate en 3.",
            },
            {
                "type": "play",
                "fen": BLOQUEO,
                "orientation": "black",
                "color": "black",
                "title": "Ahora contra Stockfish",
                "text": "Juegas con negras. Bloquea el peón y consigue las tablas.",
                "goal": "draw",
                "moves": 20,
                "hint": "Retrocede en línea recta delante del peón. Cuando dé jaque en séptima, ve a la casilla de delante.",
                "success": "Defender así un final de peones es una técnica que todo jugador debe conocer.",
            },
        ],
    },
    {
        "id": "final-peon-torre",
        "course": "finales",
        "title": "El peón de torre",
        "summary": "Si tu rey llega a la esquina de coronación del peón de torre, no hay forma de ganar.",
        "minutes": 6,
        "theme": "pawnEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": PEON_TORRE_AHOGADO,
                "orientation": "black",
                "title": "La esquina salvadora",
                "text": (
                    "El peón de torre tiene un problema: solo tiene una columna al lado. Si el rey defensor llega a la "
                    "esquina, no hay forma de echarlo. Aquí el negro no está en jaque y no tiene casillas: ahogado, tablas."
                ),
                "squares": {"h8": "green", "g8": "red", "g7": "red"},
            },
            {
                "type": "choice",
                "fen": PEON_TORRE,
                "orientation": "black",
                "title": "¿Por qué es tablas?",
                "text": "Tu rey está en h8, en la esquina de coronación. ¿Por qué no puede ganar el blanco?",
                "options": [
                    {"text": "Porque no hay forma de sacar a mi rey de la esquina sin ahogarlo", "correct": True,
                     "why": "Exacto. Con un peón de otra columna, el rey atacante podría rodear al defensor por los dos lados; con el de torre, no."},
                    {"text": "Porque el peón de torre vale menos", "correct": False,
                     "why": "Vale lo mismo en principio. Lo que cambia es que solo tiene una columna vecina."},
                    {"text": "Porque me toca mover", "correct": False,
                     "why": "Aquí da igual quién mueva: con tu rey en la esquina siempre son tablas."},
                ],
            },
            {
                "type": "play",
                "fen": PEON_TORRE,
                "orientation": "black",
                "color": "black",
                "title": "Ahora contra Stockfish",
                "text": "Juegas con negras. No salgas de la esquina y haz tablas.",
                "goal": "draw",
                "moves": 15,
                "hint": "Mantén tu rey en h8, g8 o h7. No te alejes de la esquina.",
                "success": "Recuerda este final cuando vayas perdiendo: a veces solo hace falta llegar a la esquina.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con finales de peones, de tu nivel.",
                "theme": "pawnEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-lucena",
        "course": "finales",
        "title": "La posición de Lucena",
        "summary": "La posición ganadora más importante de los finales de torres: hay que construir el puente.",
        "minutes": 10,
        "theme": "rookEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": LUCENA,
                "orientation": "white",
                "title": "El problema",
                "text": (
                    "Tu peón está en séptima y tu rey delante de él, en b8. Tu torre de c1 corta al rey negro. Pero si tu "
                    "rey sale para dejar coronar al peón, la torre negra le dará jaques sin parar por los lados. La "
                    "solución se llama «construir el puente»."
                ),
                "squares": {"b7": "yellow", "b8": "yellow", "a2": "red"},
                "arrows": [["c1", "c8", "green"]],
            },
            {
                "type": "explain",
                "fen": LUCENA,
                "orientation": "white",
                "title": "El puente",
                "text": "Primero alejas aún más al rey negro y luego tu torre va a la cuarta fila para tapar los jaques.",
                "moves": [
                    {"san": "Rd1+", "text": "Jaque: el rey negro se aleja una columna más."},
                    {"san": "Ke7", "text": "Ya no puede volver a defender."},
                    {"san": "Rd4", "text": "¡La torre a la cuarta fila! Es el puente."},
                    {"san": "Ra1", "text": "Las negras esperan."},
                    {"san": "Kc7", "text": "Tu rey sale de delante del peón."},
                    {"san": "Rc1+", "text": "Empiezan los jaques."},
                    {"san": "Kb6", "text": "Tu rey baja hacia tu torre."},
                    {"san": "Rb1+", "text": "Otro jaque."},
                    {"san": "Kc6", "text": "Sigue bajando."},
                    {"san": "Rc1+", "text": "Y otro."},
                    {"san": "Kb5", "text": "Casi en la cuarta fila."},
                    {"san": "Rb1+", "text": "Último jaque…"},
                    {"san": "Rb4", "text": "…¡y la torre lo tapa! El puente está construido: el peón coronará."},
                ],
            },
            {
                "type": "choice",
                "fen": LUCENA,
                "orientation": "white",
                "title": "Recuerda",
                "text": "¿A qué fila tiene que ir tu torre para construir el puente?",
                "options": [
                    {"text": "A la cuarta", "correct": True,
                     "why": "Exacto. Desde la cuarta fila, cuando tu rey baje a la quinta, la torre tapa el último jaque."},
                    {"text": "A la séptima, junto al peón", "correct": False,
                     "why": "Desde ahí no puede tapar los jaques laterales: tu rey no tendría refugio."},
                    {"text": "A la primera, para dar jaques", "correct": False,
                     "why": "Dar jaques no sirve: lo que necesitas es un escudo para tu rey."},
                ],
            },
            {
                "type": "play",
                "fen": LUCENA,
                "orientation": "white",
                "title": "Ahora contra Stockfish",
                "text": "Gana la posición de Lucena.",
                "goal": "win",
                "moves": 30,
                "hint": "Corta al rey negro con un jaque, lleva la torre a la cuarta fila y saca tu rey hacia ella para tapar los jaques.",
                "success": "¡Ganado! Lucena es la base de casi todos los finales de torres con un peón de ventaja.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con finales de torres, de tu nivel.",
                "theme": "rookEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-philidor",
        "course": "finales",
        "title": "La posición de Philidor",
        "summary": "La defensa clave de los finales de torres: torre en tu tercera fila y, cuando avance el peón, jaques por detrás.",
        "minutes": 10,
        "theme": "rookEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": PHILIDOR,
                "orientation": "black",
                "title": "La torre en tu tercera fila",
                "text": (
                    "Juegas con negras, con un peón de menos. Tu rey está delante del peón y tu torre en tu tercera fila "
                    "(la sexta). Desde ahí impide que el rey blanco avance a sexta: sin eso, no hay forma de hacer progresos."
                ),
                "arrows": [["h6", "a6", "green"]],
                "squares": {"e8": "green", "e5": "red"},
            },
            {
                "type": "choice",
                "fen": PHILIDOR,
                "orientation": "black",
                "title": "¿Qué haces con la torre?",
                "text": "Te toca. ¿Dónde quieres tu torre?",
                "options": [
                    {"text": "Tb6: seguir en la sexta fila", "correct": True,
                     "why": "Eso es. La torre sigue cerrando la sexta y el rey blanco no puede avanzar. Stockfish: tablas."},
                    {"text": "Th1: a la primera fila ya", "correct": False,
                     "why": "¡Txh1! La torre blanca de a1 controla la primera fila y te quedas sin torre."},
                    {"text": "Th8: a la última fila, a defender", "correct": False,
                     "why": "Pasiva y además mal colocada: Ta8+ y Txh8. Una torre pasiva pierde los finales de torres."},
                ],
            },
            {
                "type": "explain",
                "fen": PHILIDOR_CLASICO,
                "orientation": "black",
                "title": "Cuando el peón llega a sexta",
                "text": (
                    "Si el blanco empuja el peón a sexta, ya no puede refugiar a su rey delante de él. Es el momento de "
                    "cambiar de plan: tu torre baja a la primera fila y da jaques por detrás."
                ),
                "moves": [
                    {"san": "e6", "text": "El peón avanza a sexta."},
                    {"san": "Rb1", "text": "¡Ahora sí! La torre se va al otro extremo, a la primera fila."},
                    {"san": "Kd6", "text": "El rey blanco intenta acercarse."},
                    {"san": "Rd1+", "text": "Jaques por detrás: el rey no tiene dónde esconderse."},
                    {"san": "Ke5", "text": "Si se acerca a tu torre…"},
                    {"san": "Re1+", "text": "…otro jaque."},
                    {"san": "Kd6", "text": "Vuelve."},
                    {"san": "Rd1+", "text": "Y así para siempre: tablas."},
                ],
            },
            {
                "type": "play",
                "fen": PHILIDOR,
                "orientation": "black",
                "color": "black",
                "title": "Ahora contra Stockfish",
                "text": "Juegas con negras. Defiende con el método de Philidor.",
                "goal": "draw",
                "moves": 25,
                "hint": "Torre en tu sexta fila hasta que el peón avance a sexta; entonces llévala a la primera y da jaques por detrás.",
                "success": "Con Philidor salvarás muchos finales de torres con un peón de menos.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con finales de torres, de tu nivel.",
                "theme": "rookEndgame",
                "count": 5,
            },
        ],
    },
    {
        "id": "final-dama-peon",
        "course": "finales",
        "title": "Dama contra peón en séptima",
        "summary": "Con jaques y clavadas obligas al rey a taparle el paso a su peón, y tu rey se acerca un paso cada vez.",
        "minutes": 9,
        "theme": "queenEndgame",
        "steps": [
            {
                "type": "explain",
                "fen": DAMA_PEON,
                "orientation": "white",
                "title": "Ganar tiempo para tu rey",
                "text": (
                    "El peón negro está a un paso de coronar y tu rey está lejos. La dama tiene que impedir la coronación "
                    "a base de jaques, hasta que el rey negro se ponga delante de su peón. Ese tiempo lo usa tu rey para acercarse."
                ),
                "moves": [
                    {"san": "Qe4+", "text": "Jaque. El rey negro tiene que decidir."},
                    {"san": "Kd1", "text": "Se pone delante de su peón: ahora el peón no puede avanzar."},
                    {"san": "Qb1+", "text": "Más jaques para mantener el control."},
                    {"san": "Ke2", "text": "Sale de delante del peón."},
                    {"san": "Qc2", "text": "La dama clava el peón y vigila d1: no puede coronar."},
                    {"san": "Ke1", "text": "El rey negro ya no puede ayudar a su peón."},
                    {"san": "Kg1", "text": "¡Es el momento! Tu rey se acerca. Repitiendo esta idea, el peón acabará cayendo."},
                ],
            },
            {
                "type": "choice",
                "fen": DAMA_PEON,
                "orientation": "white",
                "title": "El momento de acercar el rey",
                "text": "¿Cuándo puedes permitirte una jugada de rey en lugar de un jaque?",
                "options": [
                    {"text": "Cuando el peón no pueda coronar en la jugada siguiente: rey rival delante o peón clavado", "correct": True,
                     "why": "Exacto. Solo entonces tienes una jugada libre para acercar tu rey."},
                    {"text": "Desde el principio, el rey es lo más importante", "correct": False,
                     "why": "Si mueves el rey ahora, el peón corona y ya no hay nada que hacer."},
                    {"text": "Nunca: se gana solo con jaques", "correct": False,
                     "why": "La dama sola no puede ganar el peón: necesita la ayuda de su rey."},
                ],
            },
            {
                "type": "play",
                "fen": DAMA_PEON,
                "orientation": "white",
                "title": "Ahora contra Stockfish",
                "text": "Gana con la dama contra el peón en séptima.",
                "goal": "win",
                "moves": 30,
                "hint": "Con jaques y clavadas obliga al rey a colocarse delante del peón; cada vez que lo hace, acerca tu rey un paso.",
                "success": "¡Ganado! Con un peón de alfil o de torre sería distinto: lo verás en la siguiente lección.",
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con finales de damas, de tu nivel.",
                "theme": "queenEndgame",
                "count": 5,
            },
        ],
    },
]
