"""Curso «Estrategia». Formato de las lecciones: ver app/learn.py.

Las respuestas de los choice que comparan jugadas o piezas se comprobaron con Stockfish (profundidad 20)
en la misma posición; la evaluación está en el comentario de cada posición.
"""

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# Torre (5) contra alfil y caballo (6) con peones iguales: las negras van mejor (−3,3).
CUENTA = "2bq1rk1/ppp2ppp/2n5/8/8/8/PPP2PPP/R2Q1RK1 w - - 0 1"
# Torre y alfil atacan el caballo de d5: Axd5 (+0,3 tras ganar el peón) frente a Txd5 (−2,0).
VALOR = "r1b2rk1/ppq2ppp/4p3/3n4/2B5/2P2N2/PP2QPPP/3R1RK1 w - - 0 1"
# Axa8 Dxa8 gana la calidad: +1,3 frente a +0,5 de la siguiente.
CALIDAD = "r2q1rk1/p2bbppp/1p2pn2/2p5/8/2NP2P1/PP2PPBP/R1BQ1RK1 w - - 0 1"
# Caballo bueno en d5 contra alfil malo en e7: +1,1; tras Cxe7 Rxe7, −0,2.
CAB_D5 = "1r3k2/4bppp/p2p4/1p1Np3/4P3/8/PPP2PPP/3R2K1 w - - 0 1"
# El mismo esquema con el caballo aún en c3: Cd5 es de lo mejor (+1,1).
CAB_C3 = "1r4k1/4bppp/p2p4/1p2p3/4P3/2N5/PPP2PPP/3R2K1 w - - 0 1"
# Peón pasado en a4 y peones en el otro flanco: con alfil en c2, +4,5; con caballo en c2, +2,5.
PAS_ALFIL = "8/5kpp/5p2/2n5/P7/5P2/2B3PP/5K2 w - - 0 1"
# Pareja blanca (d3 y f4): las negras la rompen con Cxd3+ (+0,8 para ellas) frente a a6 (0,0) o Cc6 (−0,2).
PAREJA = "r2q1rk1/pp2bppp/4pn2/3p4/1n1P1B2/3BPN2/PP3PPP/R2QK2R b KQ - 0 1"
# Nimzoindia tras 9.bxc3: pareja de alfiles blanca a cambio de peones doblados.
NIMZO = "r1bq1rk1/pp3ppp/2n1pn2/2pp4/2PP4/P1PBPN2/5PPP/R1BQ1RK1 b - - 0 9"
# Francesa: alfil de c8 malo (peones d5 y e6 en claras), alfil de f1 bueno.
FRANCESA = "rnb1k2r/pppnqppp/4p3/3pP3/3P4/2N5/PPP2PPP/R2QKBNR w KQkq - 0 7"
# Francesa tras 1.e4 e6 2.d4 d5 3.e5 b6 4.c3: 4…Aa6? pierde (5.Axa6 Cxa6 6.Da4+, −4,8); 4…Dd7 primero (−0,9).
FRANCESA_PLAN = "rnbqkbnr/p1p2ppp/1p2p3/3pP3/3P4/2P5/PP3PPP/RNBQKBNR b KQkq - 0 4"
# Columna semiabierta: no hay peón blanco en la columna e, sí el peón negro de e5.
SEMI = "r1b1k3/ppp2ppp/5n2/4p3/3P4/2N5/PPP2PPP/2B1R1K1 w - - 0 1"
# Columna d abierta: Td1 (+0,5) frente a Tc1 (−0,2) o Te1 (−0,1).
ABIERTA = "5rk1/pp3ppp/2p5/4p3/4P3/2P5/PP3PPP/R5K1 w - - 0 1"
# Dos torres blancas dobladas en la columna e.
DOBLES = "r2r2k1/ppp2ppp/3p4/8/3P4/2P5/PP2RPPP/4R1K1 w - - 0 1"
# Torre en séptima: Txb7 (+1,4) frente a Txf7?? (−6,4).
SEPTIMA = "r5k1/1p2Rpp1/p6p/8/8/8/PP3PPP/6K1 w - - 0 1"
# Puesto avanzado en d5: Cd5 (+2,3) frente a Cb5 (+1,5) y Ca4 (+0,7).
AVANZADO = "r1b2rk1/ppq2ppp/2n5/8/4P3/2N5/PP2QPPP/R1B2RK1 w - - 0 1"
# Peón retrasado en d3: c4 y e4 están por delante y d4 la controla el peón de e5.
RETRASADO = "6k1/ppp2ppp/3p4/4p3/2P1P3/3P4/PP3PPP/6K1 w - - 0 1"
# Solo d5 es pasado entre los peones blancos.
CUAL_PASADO = "6k1/pp3ppp/8/3P4/8/8/PP3PPP/6K1 w - - 0 1"
# Dos peones pasados unidos (+8,8).
UNIDOS = "8/5kpp/8/3PP3/8/8/5KPP/8 w - - 0 1"
# Peón pasado con la torre detrás.
TORRE_DETRAS = "2k5/8/4P3/8/8/8/8/4R1K1 w - - 0 1"
# Peón pasado alejado: las blancas ganan (+8) desviando al rey negro con el peón de a.
ALEJADO = "8/8/4k1p1/7p/P3K2P/6P1/8/8 w - - 0 1"
# Peón pasado d5 bloqueado por el caballo negro de d6.
BLOQUEO = "6k1/8/3n4/3P4/8/8/8/6K1 w - - 0 1"

# Francesa tras 3.e5: espacio blanco; 3…c5 (−0,2) frente a 3…Cc6 (−0,9) y 3…f6 (−1,3).
FR3 = "rnbqkbnr/ppp2ppp/4p3/3pP3/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 3"
# Francesa tras 5.Cf3: 5…Db6 (−0,3) frente a 5…f6 (−0,65).
FR5 = "r1bqkbnr/pp3ppp/2n1p3/2ppP3/3P4/2P2N2/PP3PPP/RNBQKB1R b KQkq - 1 5"
# Dragón con …h5: gxh5 (+3,4) frente a a3 (+2,1).
DRAGON_H = "r4rk1/pp1bppb1/3p1np1/q6p/3BP1P1/2N2P2/PPPQ4/1K1R1B1R w - - 0 15"
# Estructura Carlsbad: b4 (+0,1) frente a e4 (−1,7) y g4 (−1,9).
CARLSBAD = "2r2rk1/pp2bppp/2p1bn2/3p4/3P4/2NBPN2/PP3PPP/1R3RK1 w - - 0 15"
# Tras el ataque de minorías: peón débil en c6 en la columna c.
CARLSBAD_FIN = "2r2rk1/p3bppp/2p1bn2/3p4/3P4/3BPN2/P3NPPP/2R2RK1 w - - 0 20"
# Dragón yugoslavo con enroques opuestos: g4 (+1,4) frente a Ae2 (+0,8) y a3 (+0,6).
YUGO = "r2q1rk1/pp1bppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/2KR1B1R w - - 3 10"

LESSONS = [
    {
        "id": "valor-piezas",
        "course": "estrategia",
        "title": "Valor de las piezas",
        "summary": "Cuenta el material para decidir los cambios… y aprende cuándo los números mienten.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "La tabla de valores",
                "text": (
                    "Peón 1, caballo 3, alfil 3, torre 5 y dama 9. El rey no tiene valor: no se puede cambiar, "
                    "porque perderlo es perder la partida. Estos números son tu calculadora para decidir si un "
                    "cambio te conviene."
                ),
                "squares": {"e2": "blue", "b1": "green", "c1": "green", "a1": "yellow", "d1": "red"},
            },
            {
                "type": "choice",
                "fen": CUENTA,
                "orientation": "white",
                "title": "Cuenta",
                "text": "Las dos damas y los peones se compensan. Cuenta el resto: ¿quién tiene más material?",
                "options": [
                    {"text": "Las blancas", "correct": False,
                     "why": "Tienes dos torres (10), pero las negras tienen torre, alfil y caballo (11)."},
                    {"text": "Están igualados", "correct": False,
                     "why": "Casi: torre contra alfil y caballo es 5 contra 6. Las negras van un punto por delante."},
                    {"text": "Las negras, por un punto", "correct": True,
                     "why": "Eso es: 5 contra 6. Y en la práctica es más que un punto: con muchas piezas en el tablero, "
                            "dos piezas menores suelen ser mejores que una torre. Stockfish da a las negras más de 3 peones de ventaja."},
                ],
            },
            {
                "type": "choice",
                "fen": VALOR,
                "orientation": "white",
                "title": "¿Con qué tomas?",
                "text": "Tu torre de d1 y tu alfil de c4 atacan el caballo de d5, que solo defiende el peón de e6. ¿Con qué capturas?",
                "options": [
                    {"text": "Con la torre: Txd5", "correct": False,
                     "why": "Tras …exd5 has dado una torre (5) por un caballo (3). Pierdes dos puntos."},
                    {"text": "Con el alfil: Axd5", "correct": True,
                     "why": "Alfil por caballo es un cambio igualado, y después de …exd5 tu torre se come el peón. "
                            "Regla: captura primero con la pieza que menos vale."},
                ],
            },
            {
                "type": "explain",
                "fen": VALOR,
                "orientation": "white",
                "title": "La cuenta, jugada a jugada",
                "text": "Así queda la cuenta del cambio bueno.",
                "moves": [
                    {"san": "Bxd5", "text": "Alfil por caballo: 3 por 3. Todavía nadie gana nada."},
                    {"san": "exd5", "text": "El peón recaptura y queda solo en d5, atacado por tu torre."},
                    {"san": "Rxd5", "text": "La torre se lo come: un peón de ventaja sin dar nada a cambio."},
                ],
            },
            {
                "type": "choice",
                "fen": CALIDAD,
                "orientation": "white",
                "title": "Ganar la calidad",
                "text": (
                    "Tu alfil de g2 apunta a la torre de a8. Si la tomas, la dama negra recaptura. "
                    "¿Te interesa Axa8?"
                ),
                "arrows": [["g2", "a8", "green"]],
                "options": [
                    {"text": "Sí: das 3 y te llevas 5", "correct": True,
                     "why": "Exacto. Cambiar una pieza menor por una torre se llama «ganar la calidad»: dos puntos de "
                            "ventaja. Para Stockfish es claramente la mejor jugada."},
                    {"text": "No: es un cambio y los cambios no ganan nada", "correct": False,
                     "why": "Un cambio gana o pierde según lo que entregas y lo que recibes. Aquí das un alfil (3) "
                            "por una torre (5)."},
                    {"text": "No: el alfil de g2 defiende a tu rey", "correct": False,
                     "why": "Defiende algo, pero dos puntos de material pesan mucho más. Tu rey sigue bien protegido."},
                ],
            },
        ],
    },
    {
        "id": "alfil-caballo",
        "course": "estrategia",
        "title": "Alfil contra caballo",
        "summary": "Los dos valen 3, pero rinden muy distinto según la posición. Aprende a elegir.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": PAS_ALFIL,
                "orientation": "white",
                "title": "El alfil, a larga distancia",
                "text": (
                    "Con la posición abierta y peones en los dos flancos, el alfil brilla. Desde c2 protege tu peón "
                    "pasado de a4 y, a la vez, ataca el peón de h7 en la otra punta del tablero. El caballo negro "
                    "tiene que elegir: solo puede estar en un sitio."
                ),
                "arrows": [["c2", "a4", "green"], ["c2", "h7", "green"]],
                "squares": {"a4": "blue", "h7": "red"},
            },
            {
                "type": "choice",
                "fen": PAS_ALFIL,
                "orientation": "white",
                "title": "¿Lo cambiarías?",
                "text": "Imagina que pudieras cambiar tu alfil de c2 por un caballo en la misma casilla. ¿Lo harías?",
                "options": [
                    {"text": "No: aquí el alfil es mejor", "correct": True,
                     "why": "Bien visto. Stockfish da +4,5 con el alfil y solo +2,5 con un caballo en c2. El caballo tarda "
                            "varias jugadas en ir de un flanco al otro; el alfil llega en una."},
                    {"text": "Sí: el caballo salta por encima de los peones", "correct": False,
                     "why": "Eso ayuda en posiciones cerradas. Aquí está todo abierto y la pieza de largo alcance es el alfil."},
                    {"text": "Me da igual: los dos valen 3", "correct": False,
                     "why": "En puntos sí, pero en esta posición la diferencia es de dos peones según Stockfish."},
                ],
            },
            {
                "type": "explain",
                "fen": CAB_D5,
                "orientation": "white",
                "title": "El caballo, en lo cerrado",
                "text": (
                    "Ahora al revés. Los peones negros de d6 y e5 están fijos en casillas oscuras, y el alfil negro "
                    "de e7, que también es de oscuras, choca contra ellos. Tu caballo, en d5, no lo puede echar "
                    "ningún peón: es un pulpo en el centro del tablero."
                ),
                "squares": {"d5": "green", "e7": "red", "d6": "yellow", "e5": "yellow"},
            },
            {
                "type": "choice",
                "fen": CAB_D5,
                "orientation": "white",
                "title": "¿Cambias?",
                "text": "Puedes jugar Cxe7, y el rey negro recaptura. Caballo por alfil: 3 por 3. ¿Lo haces?",
                "options": [
                    {"text": "Sí, es un cambio justo", "correct": False,
                     "why": "En puntos sí, pero cambias tu mejor pieza por la peor del rival. Stockfish pasa de +1,1 a "
                            "un final igualado."},
                    {"text": "No: mi caballo vale mucho más que su alfil", "correct": True,
                     "why": "Eso es. Mientras el caballo siga en d5 y el alfil encerrado, las blancas juegan con una pieza "
                            "de más en la práctica."},
                ],
            },
        ],
    },
    {
        "id": "pareja-alfiles",
        "course": "estrategia",
        "title": "La pareja de alfiles",
        "summary": "Dos alfiles juntos cubren todo el tablero. Aprovéchala si la tienes y rómpela si la tiene el rival.",
        "minutes": 8,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": NIMZO,
                "orientation": "white",
                "title": "La pareja",
                "text": (
                    "Las blancas tienen los dos alfiles: el de c1 va por casillas oscuras y el de d3 por claras. "
                    "Juntos no dejan ninguna casilla sin vigilar. A cambio, sus peones de c3 y c4 están doblados: las "
                    "negras entregaron su alfil para provocarlo. Fíjate: el alfil de c1 aún está tapado por e3."
                ),
                "arrows": [["d3", "h7", "green"]],
                "squares": {"c3": "red", "c4": "red"},
            },
            {
                "type": "choice",
                "fen": NIMZO,
                "orientation": "white",
                "title": "El plan con la pareja",
                "text": "Si tienes la pareja de alfiles, ¿qué te conviene hacer con los peones del centro?",
                "options": [
                    {"text": "Abrir el centro con rupturas como e4", "correct": True,
                     "why": "Eso es. Cada línea que se abre es una diagonal más para tus alfiles, y aquí además libera el "
                            "alfil de c1. Con el centro abierto, la pareja suele valer medio peón o más."},
                    {"text": "Cerrarlo y que no se mueva nada", "correct": False,
                     "why": "Con el centro cerrado los alfiles chocan con los peones y los caballos se encuentran cómodos."},
                    {"text": "Cambiar un alfil cuanto antes", "correct": False,
                     "why": "Entonces regalas la ventaja: la fuerza está en tener los dos."},
                ],
            },
            {
                "type": "explain",
                "fen": PAREJA,
                "orientation": "black",
                "title": "Cuando la tiene el rival",
                "text": (
                    "Juegas con negras. Las blancas tienen la pareja (d3 y f4) y tú, alfil y dos caballos. "
                    "Tu caballo de b4 ataca al alfil de d3."
                ),
                "arrows": [["b4", "d3", "red"]],
                "squares": {"d3": "yellow", "f4": "yellow"},
            },
            {
                "type": "choice",
                "fen": PAREJA,
                "orientation": "black",
                "title": "¿Qué haces?",
                "text": "¿Cuál es la mejor jugada para las negras?",
                "options": [
                    {"text": "Cxd3+: cambiar el caballo por su alfil", "correct": True,
                     "why": "Exacto. Rompes la pareja: caballo por alfil, 3 por 3, pero el alfil vale más aquí. Para Stockfish "
                            "es la mejor jugada, casi un peón mejor que las demás."},
                    {"text": "a6: reforzar el flanco de dama", "correct": False,
                     "why": "Es una jugada útil, pero deja que las blancas conserven la pareja (Ae2). Stockfish: igualdad."},
                    {"text": "Cc6: retirar el caballo", "correct": False,
                     "why": "Pierdes un tiempo y las blancas siguen con sus dos alfiles. Es la peor de las tres."},
                ],
            },
        ],
    },
    {
        "id": "alfil-bueno-malo",
        "course": "estrategia",
        "title": "Alfil bueno y alfil malo",
        "summary": "Un alfil encerrado por sus propios peones apenas juega. Aprende a reconocerlo y a deshacerte de él.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": FRANCESA,
                "orientation": "white",
                "title": "El alfil malo",
                "text": (
                    "En la Francesa, los peones negros de d5 y e6 están en casillas claras, igual que el alfil de c8. "
                    "Sus propios peones le cierran las diagonales: es un alfil malo. Las negras sufren con él toda la partida."
                ),
                "squares": {"d5": "yellow", "e6": "yellow", "c8": "red"},
            },
            {
                "type": "select",
                "fen": FRANCESA,
                "orientation": "white",
                "title": "Encuéntralo",
                "text": "Pulsa el alfil malo de esta posición.",
                "answer": "c8",
                "wrong": {
                    "f1": "Ese es tu alfil bueno: tus peones de d4 y e5 están en casillas oscuras y no le estorban.",
                    "d7": "Eso es un caballo, aunque también le tapa una diagonal al alfil de c8.",
                },
                "success": "Exacto: el alfil de c8 está encerrado por sus peones de d5 y e6, y por su caballo de d7.",
            },
            {
                "type": "explain",
                "fen": FRANCESA,
                "orientation": "white",
                "title": "Y el bueno",
                "text": (
                    "Tu alfil de f1 es de casillas claras, y tus peones de d4 y e5 están en oscuras. No se estorban: "
                    "el alfil tiene toda la diagonal f1-a6 libre. La regla: pon tus peones en el color contrario al de tu alfil."
                ),
                "arrows": [["f1", "a6", "green"]],
                "squares": {"d4": "blue", "e5": "blue"},
            },
            {
                "type": "explain",
                "fen": START,
                "orientation": "black",
                "title": "Deshacerse del alfil malo",
                "text": (
                    "Si no puedes liberar al alfil malo, cámbialo por el alfil bueno del rival. En la Francesa hay un plan "
                    "clásico: …b6 y …Aa6. Avanza jugada a jugada."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e6", "text": "La Francesa: el alfil de c8 se queda dentro."},
                    {"san": "d4", "text": "Las blancas ocupan el centro."},
                    {"san": "d5", "text": "Las negras lo atacan."},
                    {"san": "e5", "text": "Las blancas cierran. Ahora d5 y e6 encierran para siempre al alfil de c8."},
                    {"san": "b6", "text": "Plan: abrir la diagonal a6-f1 para cambiar el alfil malo por el bueno blanco."},
                    {"san": "c3", "text": "Las blancas refuerzan d4."},
                    {"san": "Qd7", "text": "¡Paso previo importante! Ahora verás por qué."},
                    {"san": "Nf3", "text": "Las blancas desarrollan."},
                    {"san": "Ba6", "text": "El alfil malo sale a ofrecer el cambio."},
                    {"san": "Bxa6", "text": "Las blancas aceptan."},
                    {"san": "Nxa6", "text": "Hecho: las negras se han quitado su peor pieza y las blancas su mejor alfil."},
                ],
            },
            {
                "type": "choice",
                "fen": FRANCESA_PLAN,
                "orientation": "black",
                "title": "El orden importa",
                "text": "Tras 1.e4 e6 2.d4 d5 3.e5 b6 4.c3, quieres cambiar tu alfil malo. ¿Juegas ya 4…Aa6?",
                "arrows": [["c8", "a6", "yellow"]],
                "options": [
                    {"text": "Sí, 4…Aa6 ya", "correct": False,
                     "why": "¡Cuidado! 5.Axa6 Cxa6 6.Da4+ da jaque y se come el caballo de a6. Stockfish: casi 5 peones "
                            "de desventaja."},
                    {"text": "No: primero 4…Dd7 y luego …Aa6", "correct": True,
                     "why": "Exacto. Con la dama en d7, a4 está controlada: después de …Aa6 y los cambios, el caballo de a6 "
                            "ya no cuelga."},
                ],
            },
        ],
    },
    {
        "id": "torres-columnas",
        "course": "estrategia",
        "title": "Torres en columnas abiertas",
        "summary": "Las torres necesitan columnas libres y sueñan con la séptima fila.",
        "minutes": 9,
        "theme": None,
        "steps": [
            {
                "type": "select",
                "fen": ABIERTA,
                "orientation": "white",
                "title": "Elige la columna",
                "text": "Tu torre de a1 no hace nada. ¿A qué casilla la llevas? Púlsala.",
                "answer": "d1",
                "wrong": {
                    "c1": "En la columna c está tu propio peón de c3: la torre choca con él.",
                    "e1": "En la columna e chocan los peones de e4 y e5: la torre no ve nada.",
                    "b1": "La columna b tiene peones de los dos bandos: está cerrada.",
                    "f1": "La columna f la vigila la torre negra de f8, y tu peón de f2 te tapa.",
                },
                "success": "Exacto: la columna d no tiene peones. Una torre en una columna abierta controla de punta a punta. Para Stockfish es la mejor jugada.",
            },
            {
                "type": "explain",
                "fen": SEMI,
                "orientation": "white",
                "title": "Columna semiabierta",
                "text": (
                    "En la columna e no tienes ningún peón, pero el rival tiene uno en e5. Es una columna semiabierta: "
                    "tu torre presiona ese peón desde lejos y el rival tiene que gastar piezas en defenderlo."
                ),
                "arrows": [["e1", "e5", "green"]],
                "squares": {"e5": "red"},
            },
            {
                "type": "explain",
                "fen": DOBLES,
                "orientation": "white",
                "title": "Torres dobladas",
                "text": (
                    "Dos torres en la misma columna se apoyan: si el rival cambia la de delante, la de detrás "
                    "recaptura y sigue siendo la dueña de la columna. Doblar torres es la forma de ganar una columna disputada."
                ),
                "arrows": [["e1", "e8", "green"]],
                "squares": {"e1": "blue", "e2": "blue"},
            },
            {
                "type": "explain",
                "fen": SEPTIMA,
                "orientation": "white",
                "title": "La séptima fila",
                "text": (
                    "Al final de la columna espera el premio: la séptima fila. Allí están los peones que el rival no ha "
                    "movido y su rey. Desde e7, tu torre ataca b7 y f7 a la vez."
                ),
                "arrows": [["e7", "b7", "green"], ["e7", "f7", "green"]],
                "squares": {"b7": "red", "f7": "red"},
            },
            {
                "type": "move",
                "fen": SEPTIMA,
                "orientation": "white",
                "title": "Cobra el premio",
                "text": "La torre ataca b7 y f7. Cómete el peón bueno.",
                "line": ["Rxb7"],
                "min_eval": 80,
                "hint": "Mira qué peón está defendido: el rey de g8 protege f7, pero nadie protege b7.",
                "success": "Bien: b7 no lo defendía nadie. Con Txf7?? el rey habría recapturado y perdías la torre por un peón.",
            },
        ],
    },
    {
        "id": "puestos-avanzados",
        "course": "estrategia",
        "title": "Puestos avanzados",
        "summary": "Una casilla que ningún peón rival puede atacar es el mejor sitio para tu caballo.",
        "minutes": 8,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": AVANZADO,
                "orientation": "white",
                "title": "Qué es un puesto avanzado",
                "text": (
                    "Una casilla en el campo rival que ningún peón contrario puede atacar, y mejor aún si la protege un "
                    "peón tuyo. Aquí d5: las negras no tienen peones en las columnas c ni e, y tu peón de e4 la defiende."
                ),
                "arrows": [["c3", "d5", "green"], ["e4", "d5", "blue"]],
                "squares": {"d5": "green"},
            },
            {
                "type": "choice",
                "fen": AVANZADO,
                "orientation": "white",
                "title": "¿A qué casilla saltas?",
                "text": "Tu caballo de c3 puede ir a d5, b5 o a4. ¿Cuál es el mejor salto?",
                "options": [
                    {"text": "Cd5", "correct": True,
                     "why": "El puesto avanzado: central, protegido por e4 y sin peones que lo echen. Ataca la dama de c7 y "
                            "no se moverá de ahí. Stockfish lo prefiere claramente."},
                    {"text": "Cb5", "correct": False,
                     "why": "También ataca la dama, pero después de …a6 tiene que irse: no es un puesto, es una visita."},
                    {"text": "Ca4", "correct": False,
                     "why": "Un caballo en el borde controla la mitad de casillas. Lejos del centro, casi no juega."},
                ],
            },
            {
                "type": "select",
                "fen": CAB_C3,
                "orientation": "white",
                "title": "Encuéntralo tú",
                "text": "Las negras tienen peones en d6 y e5. Pulsa la casilla que es un puesto avanzado para tus piezas.",
                "answer": "d5",
                "wrong": {
                    "f5": "Desde f5 el caballo estaría bien, pero …g6 lo echa: no es un puesto.",
                    "c4": "c4 la ataca el peón de b5.",
                    "d4": "d4 la ataca el peón de e5.",
                },
                "success": "Exacto: d5. El peón de d6 no puede atacarla (los peones capturan en diagonal) y tu peón de e4 la protege.",
            },
        ],
    },
    {
        "id": "estructuras-peones",
        "course": "estrategia",
        "title": "Estructuras de peones",
        "summary": "Aislados, doblados, retrasados e islas: las debilidades que deciden los finales.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": NIMZO,
                "orientation": "white",
                "title": "Islas de peones",
                "text": (
                    "Una isla es un grupo de peones en columnas seguidas. Las blancas tienen dos: el peón de a3 solo, "
                    "y de c3 a h2. Cuantas más islas, más peones sin vecinos que los defiendan."
                ),
                "squares": {"a3": "blue", "c3": "yellow", "c4": "yellow", "d4": "yellow", "e3": "yellow",
                            "f2": "yellow", "g2": "yellow", "h2": "yellow"},
            },
            {
                "type": "select",
                "fen": NIMZO,
                "orientation": "white",
                "title": "Un peón aislado",
                "text": "Pulsa el peón blanco aislado: el que no tiene peones propios en las columnas vecinas.",
                "answer": "a3",
                "wrong": {
                    "d4": "d4 tiene vecinos en c3, c4 y e3: no está aislado.",
                    "c3": "c3 tiene al lado el peón de d4.",
                },
                "success": "Exacto: no hay peón blanco en la columna b. Nadie puede defender a3 con un peón.",
            },
            {
                "type": "explain",
                "fen": NIMZO,
                "orientation": "white",
                "title": "Peones doblados",
                "text": (
                    "c3 y c4 están en la misma columna: doblados. No pueden defenderse entre sí y el de delante tapa al "
                    "de detrás. Las blancas los aceptaron a cambio de la pareja de alfiles: toda debilidad se puede compensar."
                ),
                "squares": {"c3": "red", "c4": "red"},
            },
            {
                "type": "explain",
                "fen": RETRASADO,
                "orientation": "white",
                "title": "El peón retrasado",
                "text": (
                    "El peón de d3 se ha quedado atrás: sus vecinos de c4 y e4 ya no pueden protegerlo. Y si avanza a d4, "
                    "el peón de e5 lo captura. Está atascado en una columna semiabierta para el rival."
                ),
                "arrows": [["e5", "d4", "red"]],
                "squares": {"d3": "red", "d4": "yellow"},
            },
            {
                "type": "select",
                "fen": RETRASADO,
                "orientation": "white",
                "title": "La casilla débil",
                "text": "Delante de un peón retrasado queda una casilla perfecta para el rival. Púlsala.",
                "answer": "d4",
                "wrong": {
                    "d5": "d5 está en el campo negro y la vigilan tus peones de c4 y e4.",
                    "d3": "Ese es el peón retrasado. La casilla débil es la de delante.",
                },
                "success": "Exacto: d4. Ningún peón blanco puede atacarla. Un caballo negro allí sería un monstruo.",
            },
        ],
    },
    {
        "id": "peon-pasado",
        "course": "estrategia",
        "title": "El peón pasado",
        "summary": "Un peón que nadie puede frenar con peones vale oro en el final. Empújalo, protégelo o bloquéalo.",
        "minutes": 10,
        "theme": "advancedPawn",
        "steps": [
            {
                "type": "select",
                "fen": CUAL_PASADO,
                "orientation": "white",
                "title": "Encuentra el pasado",
                "text": (
                    "Un peón pasado no tiene peones rivales delante, ni en su columna ni en las de al lado. "
                    "Pulsa el peón pasado de las blancas."
                ),
                "answer": "d5",
                "wrong": {
                    "a2": "Delante de a2 está el peón negro de a7: no es pasado.",
                    "b2": "Delante de b2 está el peón de b7.",
                    "f2": "Delante de f2 está el peón negro de f7: no es pasado.",
                },
                "success": "Exacto: d5. No hay peones negros en las columnas c, d ni e. Solo las piezas pueden pararlo.",
            },
            {
                "type": "explain",
                "fen": UNIDOS,
                "orientation": "white",
                "title": "Pasados y unidos",
                "text": (
                    "Dos peones pasados en columnas vecinas se protegen entre sí al avanzar. Contra un rey solo son "
                    "imparables: si toma uno, el otro corona."
                ),
                "squares": {"d5": "green", "e5": "green"},
            },
            {
                "type": "explain",
                "fen": TORRE_DETRAS,
                "orientation": "white",
                "title": "La torre, detrás",
                "text": (
                    "La regla de Tarrasch: las torres van detrás de los peones pasados. Desde e1, tu torre protege "
                    "el peón y, cuanto más avanza, más casillas controla. Delante del peón, en cambio, la torre lo frenaría."
                ),
                "arrows": [["e1", "e6", "green"]],
                "squares": {"e8": "yellow"},
            },
            {
                "type": "explain",
                "fen": ALEJADO,
                "orientation": "white",
                "title": "El pasado alejado",
                "text": (
                    "En los finales de peones, un pasado lejos del resto es un arma: arrastra al rey rival a una esquina "
                    "mientras tu rey se come los peones del otro lado. Avanza jugada a jugada."
                ),
                "moves": [
                    {"san": "a5", "text": "El peón de a corre: el rey negro tiene que ir a por él."},
                    {"san": "Kd6", "text": "El rey negro se va hacia el flanco de dama."},
                    {"san": "Kf4", "text": "Y tu rey hacia el otro lado."},
                    {"san": "Kc6", "text": "Persigue al peón."},
                    {"san": "Kg5", "text": "Tu rey ataca g6 y h5."},
                    {"san": "Kb5", "text": "El rey negro ya casi llega al peón…"},
                    {"san": "Kxg6", "text": "…pero tú te comes g6."},
                    {"san": "Kxa5", "text": "Se ha llevado el peón de a, muy lejos de la acción."},
                    {"san": "Kxh5", "text": "Y tú, h5. Tus peones de g y h coronarán mucho antes de que vuelva el rey negro."},
                ],
            },
            {
                "type": "explain",
                "fen": BLOQUEO,
                "orientation": "white",
                "title": "Bloquearlo",
                "text": (
                    "Si el pasado es del rival, bloquéalo: pon una pieza justo delante. El caballo negro de d6 es el "
                    "bloqueador ideal: el peón no lo puede atacar, y desde ahí el caballo sigue controlando casillas importantes."
                ),
                "arrows": [["d5", "d6", "red"]],
                "squares": {"d6": "green"},
            },
            {
                "type": "choice",
                "fen": BLOQUEO,
                "orientation": "black",
                "title": "El mejor bloqueador",
                "text": "Para bloquear un peón pasado, ¿qué pieza prefieres poner delante?",
                "options": [
                    {"text": "Un caballo", "correct": True,
                     "why": "Eso es. El caballo no pierde fuerza bloqueando: salta igual desde ahí. Un alfil bloqueando, "
                            "en cambio, se queda con media diagonal tapada."},
                    {"text": "La dama", "correct": False,
                     "why": "Funciona, pero atas tu pieza más valiosa a una tarea pequeña, y cualquier pieza rival la echa."},
                    {"text": "Una torre", "correct": False,
                     "why": "Una torre delante del peón queda pasiva. Las torres rinden detrás de los pasados, no delante."},
                ],
            },
            {
                "type": "practice",
                "title": "Partidas reales",
                "text": "Cinco puzzles de partidas reales con peones avanzados, de tu nivel.",
                "theme": "advancedPawn",
                "count": 5,
            },
        ],
    },
    {
        "id": "espacio-centro",
        "course": "estrategia",
        "title": "Espacio y centro",
        "summary": "Los peones avanzados quitan casillas al rival. Aprende a ganar espacio y a defenderte cuando te falta.",
        "minutes": 9,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": FR3,
                "orientation": "white",
                "title": "Un peón que quita sitio",
                "text": (
                    "Con 3.e5, las blancas tienen un peón en la quinta fila. Ese peón quita al rival dos casillas "
                    "importantes, d6 y f6, y detrás de él las piezas blancas tienen más sitio para maniobrar. Eso es "
                    "tener ventaja de espacio."
                ),
                "arrows": [["e5", "f6", "red"], ["e5", "d6", "red"]],
                "squares": {"e5": "green", "f6": "red", "d6": "red"},
            },
            {
                "type": "select",
                "fen": FR3,
                "orientation": "black",
                "title": "La casilla perdida",
                "text": "El caballo de g8 quiere salir a su casilla natural, pero el peón de e5 se la ha quitado. Púlsala.",
                "answer": "f6",
                "wrong": {
                    "h6": "h6 sigue libre, aunque en el borde el caballo vale poco.",
                    "e7": "e7 está libre: desde ahí el caballo saldrá hacia f5 o c6.",
                },
                "success": "Exacto: f6. Sin esa casilla, el caballo de g8 tendrá que buscar un camino más largo.",
            },
            {
                "type": "choice",
                "fen": FR3,
                "orientation": "black",
                "title": "Con menos espacio",
                "text": "Juegas con negras y tienes menos sitio. ¿Qué haces?",
                "options": [
                    {"text": "…c5: atacar ya el centro blanco", "correct": True,
                     "why": "Eso es. Quien tiene menos espacio tiene que atacar los peones que se lo quitan. Para Stockfish es la mejor jugada."},
                    {"text": "…Cc6: desarrollar sin más", "correct": False,
                     "why": "Desarrolla, pero el caballo tapa tu peón de c y ya no puedes atacar d4 con …c5. Stockfish: casi un peón peor."},
                    {"text": "…f6: atacar la punta ya", "correct": False,
                     "why": "Demasiado pronto: debilita e6 y tu rey, y las blancas responden con desarrollo. Stockfish: más de un peón peor."},
                ],
            },
            {
                "type": "explain",
                "fen": FR5,
                "orientation": "white",
                "title": "El plan de cada uno",
                "text": (
                    "El que tiene más espacio quiere mantenerlo y atacar en el flanco donde lo tiene: aquí las blancas, "
                    "en el flanco de rey. El que tiene menos busca cambios y presiona los peones que le ahogan: …c5, "
                    "…Cc6 y …Db6 van todos contra d4."
                ),
                "arrows": [["c5", "d4", "red"], ["c6", "d4", "red"]],
                "squares": {"d4": "red", "e5": "green"},
            },
        ],
    },
    {
        "id": "rupturas",
        "course": "estrategia",
        "title": "Rupturas de peones",
        "summary": "Un peón que se lanza contra los del rival abre columnas y diagonales. Elegir la ruptura correcta decide el plan.",
        "minutes": 9,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": FR5,
                "orientation": "black",
                "title": "Contra una cadena",
                "text": (
                    "Los peones blancos de d4 y e5 forman una cadena. Hay dos formas de romperla: atacar la base (d4), "
                    "que es la que sostiene a todos, o atacar la cabeza (e5) con …f6. La regla clásica: primero la base."
                ),
                "arrows": [["c5", "d4", "green"], ["f7", "f6", "yellow"]],
                "squares": {"d4": "red", "e5": "yellow"},
            },
            {
                "type": "select",
                "fen": FR5,
                "orientation": "black",
                "title": "La base",
                "text": "Pulsa el peón blanco que sostiene toda la cadena.",
                "answer": "d4",
                "wrong": {
                    "e5": "e5 es la cabeza: la sostiene d4. Si cae d4, e5 se queda sin apoyo.",
                    "c3": "c3 defiende d4, pero la base de la cadena d4-e5 es d4.",
                },
                "success": "Exacto: d4. Si cae d4, el peón de e5 se queda colgando.",
            },
            {
                "type": "choice",
                "fen": FR5,
                "orientation": "black",
                "title": "¿Base o cabeza?",
                "text": "Ya has jugado …c5 y …Cc6. ¿Cómo sigues?",
                "options": [
                    {"text": "…Db6: más presión sobre d4", "correct": True,
                     "why": "Bien: tres piezas contra d4 y la dama también mira b2. Stockfish la prefiere a …f6."},
                    {"text": "…f6: atacar ya la cabeza", "correct": False,
                     "why": "Todavía no: con d4 bien defendido, …f6 debilita e6 y tu rey sin ganar nada. Stockfish: peor."},
                ],
            },
            {
                "type": "explain",
                "fen": DRAGON_H,
                "orientation": "white",
                "title": "Romper para abrir líneas",
                "text": (
                    "Las rupturas no son solo cosa del centro. Aquí las negras han frenado tu ataque con …h5, pero tu "
                    "peón de g4 puede romper: gxh5 abre columnas hacia su rey, justo donde tus torres esperan."
                ),
                "arrows": [["g4", "h5", "green"]],
                "squares": {"h5": "red", "g6": "yellow"},
            },
            {
                "type": "move",
                "fen": DRAGON_H,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Rompe y abre líneas contra el rey negro.",
                "line": ["gxh5"],
                "hint": "Tu peón de g4 se come el de h5.",
                "success": "Bien: la columna h y la g se abren hacia el rey negro. Stockfish: más de 3 peones de ventaja, frente a +2 de la siguiente mejor.",
            },
        ],
    },
    {
        "id": "ataque-minorias",
        "course": "estrategia",
        "title": "El ataque de minorías",
        "summary": "Dos peones contra tres: avanzarlos parece absurdo, pero crea una debilidad permanente en el campo rival.",
        "minutes": 8,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": CARLSBAD,
                "orientation": "white",
                "title": "Dos contra tres",
                "text": (
                    "En el flanco de dama tienes dos peones (a y b) contra tres de las negras (a, b y c). Parece que "
                    "atacar con menos peones no tiene sentido… pero el plan b4-b5 obliga al rival a cambiar, y lo que "
                    "queda es un peón débil en c6 o un peón aislado en d5."
                ),
                "arrows": [["b2", "b4", "green"], ["b4", "b5", "green"]],
                "squares": {"c6": "red"},
            },
            {
                "type": "choice",
                "fen": CARLSBAD,
                "orientation": "white",
                "title": "Elige el plan",
                "text": "¿Cuál es el plan correcto para las blancas?",
                "options": [
                    {"text": "b4: el ataque de minorías", "correct": True,
                     "why": "Eso es. Para Stockfish es la mejor jugada: prepara b5 contra c6."},
                    {"text": "e4: romper en el centro", "correct": False,
                     "why": "Aquí no: tras …dxe4 las piezas se cambian y no ganas nada. Stockfish: casi 2 peones peor."},
                    {"text": "g4: atacar al rey", "correct": False,
                     "why": "Debilita tu propio rey y el alfil de e6 se come el peón. Stockfish: casi 2 peones peor."},
                ],
            },
            {
                "type": "explain",
                "fen": CARLSBAD_FIN,
                "orientation": "white",
                "title": "El objetivo cumplido",
                "text": (
                    "Así acaba el plan cuando sale bien: tras b5 y los cambios en c6, las negras se quedan con un peón en "
                    "c6 sin peones vecinos que lo defiendan, en una columna abierta para tus torres. Es un objetivo para "
                    "el resto de la partida."
                ),
                "arrows": [["c1", "c6", "green"]],
                "squares": {"c6": "red"},
            },
            {
                "type": "select",
                "fen": CARLSBAD_FIN,
                "orientation": "white",
                "title": "La debilidad",
                "text": "Pulsa el peón negro que se ha quedado débil.",
                "answer": "c6",
                "wrong": {
                    "d5": "d5 lo defiende el peón de c6. La debilidad es c6, que no tiene ningún peón que lo proteja.",
                    "a7": "a7 está lejos y no estorba a nadie. El peón débil es c6.",
                },
                "success": "Exacto: c6. Ningún peón negro puede defenderlo y tu torre de c1 ya lo ataca.",
            },
        ],
    },
    {
        "id": "enroques-opuestos",
        "course": "estrategia",
        "title": "Enroques opuestos",
        "summary": "Con los reyes en flancos distintos la partida es una carrera: gana quien abre primero el enroque rival.",
        "minutes": 9,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": YUGO,
                "orientation": "white",
                "title": "Una carrera",
                "text": (
                    "Las blancas se han enrocado largo y las negras corto. Cuando los reyes están en flancos opuestos, "
                    "avanzar los peones hacia el rey rival no debilita el tuyo. Por eso los dos lanzan sus peones: gana "
                    "quien abra antes las columnas del enroque rival."
                ),
                "arrows": [["g2", "g4", "green"], ["h2", "h4", "green"]],
                "squares": {"g8": "red", "c1": "yellow"},
            },
            {
                "type": "choice",
                "fen": YUGO,
                "orientation": "white",
                "title": "¿Qué juegas?",
                "text": "¿Cuál es la jugada que pide la posición?",
                "options": [
                    {"text": "g4: lanzar los peones contra el rey negro", "correct": True,
                     "why": "Eso es. g4 y h4 preparan h5 para abrir la columna h. Para Stockfish es de lo mejor (+1,4)."},
                    {"text": "Ae2: desarrollar tranquilamente", "correct": False,
                     "why": "En una carrera, cada jugada tranquila es un tiempo regalado al ataque rival. Stockfish: medio peón peor."},
                    {"text": "a3: proteger tu rey", "correct": False,
                     "why": "Todavía no: primero tu ataque. Mover ya los peones de tu enroque te quita tiempo y crea objetivos. Stockfish: casi un peón peor. (Más adelante, a3 sirve para frenar el avance negro.)"},
                ],
            },
            {
                "type": "explain",
                "fen": YUGO,
                "orientation": "white",
                "title": "Los dos atacan",
                "text": "Así sigue la carrera en el Dragón, con las mejores jugadas para los dos bandos.",
                "moves": [
                    {"san": "g4", "text": "Las blancas empiezan su avance."},
                    {"san": "Nxd4", "text": "Las negras cambian piezas para frenar el ataque…"},
                    {"san": "Bxd4", "text": "…y el alfil blanco se coloca en la gran diagonal."},
                    {"san": "Qa5", "text": "Las negras contraatacan contra tu rey, en el otro flanco."},
                    {"san": "h4", "text": "Las blancas siguen: el peón de h quiere llegar a h5."},
                    {"san": "Be6", "text": "Las negras desarrollan y preparan su ataque."},
                    {"san": "a3", "text": "Las blancas frenan el avance negro en el flanco de dama."},
                    {"san": "h5", "text": "Las negras ponen un peón en h5 para frenar el h5 blanco."},
                ],
            },
            {
                "type": "select",
                "fen": YUGO,
                "orientation": "white",
                "title": "El objetivo",
                "text": "Tus peones de g y h van contra el enroque negro. ¿Qué peón negro es el objetivo para abrir la columna h?",
                "answer": "g6",
                "wrong": {
                    "h7": "h7 está detrás: el que se cruza en el camino de tu peón de h es g6.",
                    "f7": "f7 está lejos de tus peones. El objetivo es g6.",
                },
                "success": "Exacto: g6. h4-h5 y hxg6 abren la columna h hacia el rey negro.",
            },
        ],
    },
]
