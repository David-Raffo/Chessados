"""Curso «Principios de apertura». Formato de las lecciones: ver app/learn.py."""

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Sacrificio en h7 que funciona: Axh7+ (+3,1) frente a Ab1 (+1,2).
GRIEGO = "r1bq1rk1/pp1n1ppp/2n1p3/3pP3/1b1P4/2NB1N2/PP3PPP/R1BQK2R w KQ - 0 8"
# Con el caballo en f6 defendiendo h7: Axh7+ (−4,8) frente a Cbd2 (−0,2).
GRIEGO_CF6 = "r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP3PPP/RNBQ1RK1 w - - 0 9"
# La misma posición que GRIEGO con el caballo en d2: Axh7+ (−3,1) frente a Cf3 (+0,5).
GRIEGO_SIN_CABALLO = "r1bq1rk1/pp1n1ppp/2n1p3/3pP3/1b1P4/2NB4/PP1N1PPP/R1BQK2R w KQ - 0 8"
# Rey negro en e8 y alfil suelto en b4: Da4+ (+4,0) frente a O-O (−1,8) y Ad2 (−1,8).
CENTRO_DA4 = "r2qk2r/ppp2ppp/5n2/3p4/1bn5/2N1PB2/PP3PPP/R1BQK2R w KQkq - 2 10"
# Rey blanco en e1 y alfil suelto en b5: …Da5+.
CENTRO_DA5 = "r1bqk2r/pp3ppp/2nbp3/1B2N3/3PpP2/4P3/PP4PP/R1BQK2R b KQkq - 1 10"
# Damas enfrentadas y rey negro en e8: Dxd8+ y Cxf7+.
CENTRO_HORQ = "rn1qkbnr/ppp1ppp1/7p/6N1/8/3Q4/PPP2PPP/RNB1K2R w KQkq - 0 7"

LESSONS: list[dict] = [
    {
        "id": "desarrollo-centro",
        "course": "aperturas",
        "title": "Desarrollo y centro",
        "summary": "Ocupa el centro con peones, saca antes las piezas menores que la dama y conecta las torres.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "Una apertura sana",
                "text": (
                    "Mira cómo se juega una apertura sana: pocas jugadas, cada pieza sale una vez y el centro "
                    "queda ocupado. Avanza jugada a jugada y fíjate en el porqué de cada una."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro. Controla d5 y f5 y abre la diagonal del alfil de f1."},
                    {"san": "e5", "text": "Las negras responden igual: también ocupan el centro."},
                    {"san": "Nf3", "text": "El caballo ataca e5 y deja libre g1 para enrocar."},
                    {"san": "Nc6", "text": "El caballo negro sale y apunta a d4 y e5."},
                    {"san": "Bc4", "text": "Alfil a una diagonal activa que apunta a f7."},
                    {"san": "Nf6", "text": "Las negras presionan e4 con el caballo."},
                    {"san": "d3", "text": "Defiende e4 y deja salir el alfil de c1."},
                    {"san": "Bc5", "text": "El alfil negro también sale a una diagonal buena."},
                    {"san": "c3", "text": "Prepara d4 para tener dos peones en el centro."},
                    {"san": "d6", "text": "Las negras refuerzan el centro con el peón."},
                    {"san": "O-O", "text": "Enroque corto: el rey se pone a salvo y la torre entra en juego en f1."},
                ],
            },
            {
                "type": "explain",
                "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
                "orientation": "white",
                "title": "El centro",
                "text": (
                    "Estas son las cuatro casillas del centro: d4, d5, e4 y e5. Quien las controla tiene más "
                    "sitio para sus piezas, y el rival lo tiene más difícil para atacar."
                ),
                "squares": {"d4": "green", "d5": "green", "e4": "green", "e5": "green"},
            },
            {
                "type": "select",
                "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
                "orientation": "white",
                "title": "Desarrolla el caballo",
                "text": "Ya tienes e4 y las negras tienen e5. Pulsa la casilla donde desarrollarías el caballo de g1.",
                "answer": "f3",
                "wrong": {
                    "h3": "Llega, pero el caballo queda en el borde y casi no toca el centro.",
                },
                "success": "Exacto: Cf3 ataca e5, apoya el centro y deja libre g1 para enrocar.",
            },
            {
                "type": "choice",
                "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
                "orientation": "white",
                "title": "¿Qué jugada sigue?",
                "text": "Tienes e4 y Cf3, y las negras tienen Cc6. ¿Cuál jugada sigue los principios?",
                "options": [
                    {"text": "3.Ac4", "correct": True,
                     "why": "Saca el alfil a una diagonal activa que apunta a f7 y prepara el enroque. "
                            "Cada pieza sale una vez y con un objetivo."},
                    {"text": "3.h3", "correct": False,
                     "why": "Mueve un peón del borde sin desarrollar nada. Pierdes tiempo mientras el rival saca sus piezas."},
                    {"text": "3.a3", "correct": False,
                     "why": "Otro peón del borde sin plan. Las piezas siguen en casa y esa jugada no las ayuda."},
                ],
            },
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "Mover la misma pieza, con motivo",
                "text": (
                    "El alfil blanco se mueve tres veces en la Ruy López y es una apertura excelente. Mover dos "
                    "veces la misma pieza es un error solo cuando no tiene motivo."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e5", "text": "Las negras responden en el centro."},
                    {"san": "Nf3", "text": "Caballo que ataca e5."},
                    {"san": "Nc6", "text": "Las negras defienden e5 con el caballo."},
                    {"san": "Bb5", "text": "El alfil ataca al caballo de c6, que defiende e5."},
                    {"san": "a6", "text": "Las negras le preguntan qué quiere hacer."},
                    {"san": "Ba4", "text": "Se retira, pero sigue en la diagonal hacia c6. No ha perdido nada."},
                    {"san": "Nf6", "text": "Las negras atacan e4."},
                    {"san": "O-O", "text": "Enroque: el rey a salvo y la torre en f1, lista para ir al centro."},
                    {"san": "Be7", "text": "Las negras sacan el alfil y preparan su enroque."},
                    {"san": "Re1", "text": "La torre se sitúa en la columna e, presionando el centro."},
                    {"san": "b5", "text": "Las negras atacan al alfil de a4."},
                    {"san": "Bb3", "text": "Otra retirada, esta vez a una casilla segura, y el alfil sigue en juego."},
                    {"san": "d6", "text": "Las negras defienden e5 y cierran el centro."},
                ],
            },
            {
                "type": "explain",
                "fen": "r1bqk2r/ppp2ppp/2np1n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQ1RK1 b kq - 1 6",
                "orientation": "white",
                "title": "Conectar las torres",
                "text": (
                    "Las torres están separadas por el caballo de b1, el alfil de c1 y la dama de d1. Para conectarlas "
                    "hay que sacar esas tres piezas. Entonces la torre de a1 llega a f1 sin estorbos."
                ),
                "arrows": [["a1", "f1", "green"]],
                "squares": {"b1": "red", "c1": "red", "d1": "red"},
            },
        ],
    },
    {
        "id": "cuando-enrocar",
        "course": "aperturas",
        "title": "Cuándo enrocar",
        "summary": "Enroca pronto para proteger al rey y activar la torre, pero solo si se cumplen las condiciones.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 1 5",
                "orientation": "white",
                "title": "El enroque corto",
                "text": (
                    "Enrocar es mover el rey dos casillas y pasar la torre al otro lado: el rey de e1 va a g1 y la "
                    "torre de h1 a f1. Aquí f1 y g1 ya están libres, así que se puede hacer ahora."
                ),
                "arrows": [["e1", "g1", "green"], ["h1", "f1", "green"]],
                "squares": {"f1": "blue", "g1": "blue"},
            },
            {
                "type": "choice",
                "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
                "orientation": "white",
                "title": "¿Puedes enrocar aquí?",
                "text": "Rey y torre no se han movido. ¿Puedes enrocar corto ahora?",
                "options": [
                    {"text": "Sí, O-O", "correct": False,
                     "why": "Rey y torre no se han movido, pero el alfil de f1 sigue en su casilla. Para enrocar "
                            "corto, f1 y g1 tienen que estar vacías."},
                    {"text": "No: el alfil de f1 sigue en medio", "correct": True,
                     "why": "Eso es. El alfil ocupa f1, y esa casilla tiene que estar libre para que la torre pase."},
                    {"text": "No: el rey ya ha salido del centro", "correct": False,
                     "why": "El rey sigue en e1 y no se ha movido. Lo que falta es vaciar f1."},
                ],
            },
            {
                "type": "choice",
                "fen": "4k2r/8/b7/8/8/8/8/4K2R w K - 0 1",
                "orientation": "white",
                "title": "Casillas atacadas",
                "text": (
                    "Ahora rey y torre están en su sitio y f1 y g1 están libres. Pero el alfil negro de a6 domina "
                    "la diagonal que llega a f1. ¿Puede enrocar el blanco?"
                ),
                "options": [
                    {"text": "Sí, O-O", "correct": False,
                     "why": "El rey pasaría por f1, y esa casilla no puede estar atacada. El alfil de a6 la controla."},
                    {"text": "No: f1 está atacada por el alfil de a6", "correct": True,
                     "why": "Eso es. Durante el enroque el rey no puede pasar por una casilla atacada, y f1 lo está."},
                    {"text": "No: el rey está en jaque", "correct": False,
                     "why": "El rey no está en jaque: el alfil no lo ataca. El motivo es la casilla f1."},
                ],
            },
            {
                "type": "select",
                "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
                "orientation": "white",
                "title": "Lo que impide el enroque",
                "text": "Ni rey ni torre se han movido. Pulsa la casilla que impide el enroque corto.",
                "answer": "f1",
                "wrong": {
                    "h1": "La torre de h1 no estorba: se queda en su sitio para el enroque.",
                    "g1": "g1 ya está libre. Lo que estorba es el alfil de f1, que ocupa la casilla por la que pasa la torre.",
                },
                "success": "Exacto: el alfil de f1 tiene que salir antes de poder enrocar.",
            },
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "Enroca pronto",
                "text": (
                    "Las dos partes enrocan en pocas jugadas: el rey queda a salvo y la torre entra en juego. "
                    "Fíjate en el orden: primero las piezas menores, después el enroque."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e5", "text": "Las negras responden igual."},
                    {"san": "Nf3", "text": "Caballo que ataca e5 y libera g1."},
                    {"san": "Nc6", "text": "Las negras desarrollan."},
                    {"san": "Bc4", "text": "El alfil sale de f1: ya no estorba el enroque."},
                    {"san": "Bc5", "text": "El alfil negro también sale."},
                    {"san": "c3", "text": "Prepara el centro con d4."},
                    {"san": "Nf6", "text": "Las negras presionan e4."},
                    {"san": "d3", "text": "Defiende e4 y deja salir el alfil de c1."},
                    {"san": "d6", "text": "Las negras refuerzan el centro."},
                    {"san": "O-O", "text": "Enroque blanco: rey a g1 en la sexta jugada."},
                    {"san": "O-O", "text": "Enroque negro: también a salvo, con la torre en f8."},
                ],
            },
            {
                "type": "explain",
                "fen": "r2qkb1r/ppp2ppp/2n1pn2/3p1b2/3P1B2/2N2N2/PPPQPPPP/R3KB1R w KQkq - 2 6",
                "orientation": "white",
                "title": "El enroque largo",
                "text": (
                    "El largo mueve el rey de e1 a c1 y la torre de a1 a d1. Por el camino el rey cruza d1, así que "
                    "d1 y c1 no pueden estar atacadas. Además, b1 tiene que estar libre."
                ),
                "arrows": [["e1", "c1", "green"], ["a1", "d1", "green"]],
                "squares": {"b1": "blue", "c1": "blue", "d1": "blue"},
            },
            {
                "type": "choice",
                "fen": "r2qkb1r/ppp2ppp/2n1pn2/3p1b2/3P1B2/2N2N2/PPPQPPPP/R3KB1R w KQkq - 2 6",
                "orientation": "white",
                "title": "¿Y el largo?",
                "text": "Mira la posición de arriba. ¿Puede el blanco hacer O-O-O?",
                "options": [
                    {"text": "Sí, O-O-O", "correct": True,
                     "why": "b1, c1 y d1 están libres, el rey no está en jaque y ninguna casilla que cruza está atacada."},
                    {"text": "No: b1 sigue ocupada", "correct": False,
                     "why": "b1 está libre: el caballo de b1 ya salió a c3. Solo tiene que estar vacía."},
                    {"text": "No: la torre de a1 ya se ha movido", "correct": False,
                     "why": "La torre de a1 sigue en su casilla: no se ha movido."},
                ],
            },
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "El peligro del rey en el centro",
                "text": (
                    "Con el centro abierto, el rey que sigue en e1 recibe jaques. Aquí el alfil de b4 da jaque. "
                    "No se puede enrocar estando en jaque, así que hay que tapar con Ad2."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e5", "text": "Las negras responden igual."},
                    {"san": "Nf3", "text": "Caballo que ataca e5."},
                    {"san": "Nc6", "text": "Las negras desarrollan."},
                    {"san": "Bc4", "text": "El alfil apunta a f7."},
                    {"san": "Bc5", "text": "Las negras también sacan el alfil."},
                    {"san": "c3", "text": "Prepara d4."},
                    {"san": "Nf6", "text": "Las negras presionan e4."},
                    {"san": "d4", "text": "Ocupa el centro, pero abre la posición."},
                    {"san": "exd4", "text": "Las negras cambian en d4 y el centro empieza a abrirse."},
                    {"san": "cxd4", "text": "Recuperan el peón y el centro sigue abierto."},
                    {"san": "Bb4+", "text": "Jaque desde b4: la diagonal llega hasta e1."},
                    {"san": "Bd2", "text": "Tapa el jaque. No se puede enrocar en jaque."},
                    {"san": "Bxd2+", "text": "Las negras cambian alfiles, con jaque otra vez."},
                    {"san": "Nbxd2", "text": "El caballo recupera la pieza y el rey ya no está en jaque."},
                ],
            },
            {
                "type": "explain",
                "fen": "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQ1RK1 w - - 2 7",
                "orientation": "white",
                "title": "Los peones del enroque",
                "text": (
                    "Tras enrocar, los peones f2, g2 y h2 protegen al rey. Adelantarlos sin motivo abre líneas hacia él. "
                    "Muévelos solo si tienes un plan claro."
                ),
                "squares": {"f2": "green", "g2": "green", "h2": "green"},
            },
        ],
    },
    {
        "id": "dama-pronto",
        "course": "aperturas",
        "title": "No saques la dama pronto",
        "summary": "Una dama sacada en las primeras jugadas pierde tiempos: el rival la ataca y ella tiene que volver a moverse.",
        "minutes": 8,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "La dama sale y el rival gana tiempo",
                "text": (
                    "Mira cómo la dama blanca se mueve dos veces mientras las negras sacan piezas con tempo. "
                    "Cada jugada de la dama tiene que valer más que el desarrollo del rival."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e5", "text": "Las negras responden en el centro."},
                    {"san": "Qh5", "text": "La dama ataca e5 y f7. Pero sale pronto y queda expuesta."},
                    {"san": "Nc6", "text": "Las negras desarrollan y defienden e5."},
                    {"san": "Bc4", "text": "El alfil apoya el ataque a f7."},
                    {"san": "g6", "text": "El peón ataca la dama y la obliga a moverse otra vez."},
                    {"san": "Qf3", "text": "La dama se retira. Ya van dos movimientos con la misma pieza."},
                    {"san": "Nf6", "text": "El caballo sale y tapa el ataque a f7. Las negras van por delante en desarrollo."},
                ],
            },
            {
                "type": "select",
                "fen": "rnbqkbnr/pppp1ppp/8/4p2Q/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 2",
                "orientation": "black",
                "title": "Tu turno, con negras",
                "text": (
                    "Tu rival ha sacado la dama a h5: ataca tu peón de e5. Juegas con negras. ¿A qué casilla "
                    "llevas un caballo para defender e5 y desarrollar a la vez?"
                ),
                "answer": "c6",
                "wrong": {
                    "f6": "Cf6 ataca la dama, pero deja e5 sin defensa: 3.Dxe5+ se lleva un peón con jaque.",
                    "h6": "Desde h6 el caballo no defiende e5 y se queda en el borde.",
                    "e7": "Desde e7 el caballo no defiende e5.",
                },
                "success": "Exacto: Cc6 defiende e5 y saca una pieza. Ahora la dama blanca es un blanco para tus piezas.",
            },
            {
                "type": "explain",
                "fen": "r1bqkbnr/pppp1p1p/2n3p1/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 4",
                "orientation": "white",
                "title": "La dama, atacada otra vez",
                "text": (
                    "Tras 2…Cc6 3.Ac4 g6, un simple peón ataca la dama y tiene que moverse otra vez. Cada vez que "
                    "la dama huye, el rival gana un tiempo para sacar otra pieza."
                ),
                "arrows": [["g6", "h5", "red"]],
                "squares": {"h5": "red"},
            },
            {
                "type": "choice",
                "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
                "orientation": "white",
                "title": "Segunda jugada",
                "text": "Has jugado 1.e4 e5. ¿Qué segunda jugada sigue los principios?",
                "options": [
                    {"text": "2.Cf3", "correct": True,
                     "why": "Desarrolla un caballo y ataca e5 sin gastar la dama. Las piezas menores salen primero."},
                    {"text": "2.Dh5", "correct": False,
                     "why": "La dama sale pronto y el negro la irá atacando mientras desarrolla. Pierdes tiempos."},
                    {"text": "2.a3", "correct": False,
                     "why": "Un peón del borde no desarrolla nada y tampoco ataca."},
                ],
            },
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "La Escandinava",
                "text": (
                    "En la Escandinava las negras sacan la dama en la segunda jugada. Las blancas la atacan con "
                    "tempo y la dama tiene que volver a moverse. Pierde jugadas por el camino."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "d5", "text": "Las negras atacan el centro."},
                    {"san": "exd5", "text": "Las blancas toman el peón."},
                    {"san": "Qxd5", "text": "La dama negra recupera el peón… y sale muy pronto."},
                    {"san": "Nc3", "text": "El caballo ataca la dama con tempo."},
                    {"san": "Qa5", "text": "La dama se retira. Ya ha movido dos veces."},
                    {"san": "d4", "text": "Las blancas ocupan el centro."},
                    {"san": "Nf6", "text": "Las negras desarrollan."},
                    {"san": "Nf3", "text": "El caballo blanco sale."},
                    {"san": "c6", "text": "Las negras preparan la defensa."},
                ],
            },
            {
                "type": "select",
                "fen": "rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3",
                "orientation": "white",
                "title": "Gana tiempo",
                "text": "La dama negra ya ha salido a d5. Pulsa la casilla a la que llevas el caballo de b1 para atacarla con tempo.",
                "answer": "c3",
                "wrong": {
                    "f3": "Cf3 está bien, pero no ataca la dama y no gana tiempo.",
                    "d4": "d4 ocupa el centro, pero no ataca la dama. El tempo lo gana Cc3.",
                },
                "success": "Exacto: Cc3 ataca la dama con tempo. Otra vez tiene que moverse.",
            },
        ],
    },
    {
        "id": "trampas",
        "course": "aperturas",
        "title": "Trampas típicas",
        "summary": "Tres trampas que aparecen una y otra vez: el mate del pastor, el mate de Legal y el mate del loco.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "El mate del pastor",
                "text": (
                    "La dama y el alfil atacan f7, un punto que solo defiende el rey. Si el negro juega un movimiento "
                    "natural como Cf6, cae el mate. Mira cómo se produce."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e5", "text": "Las negras responden igual."},
                    {"san": "Bc4", "text": "El alfil apunta a f7, el punto débil de las negras."},
                    {"san": "Nc6", "text": "Las negras desarrollan."},
                    {"san": "Qh5", "text": "La dama ataca f7 junto al alfil: ahora f7 atacada dos veces."},
                    {"san": "Nf6", "text": "Un movimiento natural, porque ataca la dama. Pero deja f7 sin defensa."},
                    {"san": "Qxf7#", "text": "Mate. La dama toma f7 con jaque, el alfil la sostiene y el rey no tiene casillas libres."},
                ],
            },
            {
                "type": "choice",
                "fen": "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3",
                "orientation": "black",
                "title": "Tu defensa, con negras",
                "text": "La dama blanca amenaza el mate en f7. ¿Cómo lo evitas?",
                "options": [
                    {"text": "g6", "correct": True,
                     "why": "El peón corta la diagonal de la dama: desde h5 ya no llega a f7. Además ataca la dama."},
                    {"text": "Cf6", "correct": False,
                     "why": "Ataca la dama, pero deja f7 sin defensa: 4.Dxf7#."},
                    {"text": "d5", "correct": False,
                     "why": "Corta la diagonal del alfil, pero 4.Axd5 se lleva el peón y vuelve a apuntar a f7."},
                ],
            },
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "La trampa de Legal",
                "text": (
                    "El blanco deja su dama en d1 a tiro del alfil de g4. Si el negro la toma con 5…Axd1??, recibe "
                    "mate en dos jugadas. La lección: antes de capturar algo grande, mira qué amenaza el rival."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e5", "text": "Las negras responden en el centro."},
                    {"san": "Nf3", "text": "Caballo que ataca e5."},
                    {"san": "d6", "text": "Las negras defienden e5 con el peón."},
                    {"san": "Bc4", "text": "El alfil apunta a f7."},
                    {"san": "Bg4", "text": "El alfil negro ataca el caballo de f3."},
                    {"san": "Nc3", "text": "Las blancas desarrollan y apoyan el centro."},
                    {"san": "g6", "text": "Jugada floja: abre la puerta a la trampa."},
                    {"san": "Nxe5", "text": "¡El caballo estaba clavado y se mueve igualmente! Toma e5 y deja la dama a tiro."},
                    {"san": "Bxd1", "text": "El error grave: toma la dama. Lo correcto era 5…dxe5, perdiendo solo un peón."},
                    {"san": "Bxf7+", "text": "Jaque: el alfil toma f7 y el rey negro tiene que moverse."},
                    {"san": "Ke7", "text": "Forzado: el rey va a e7."},
                    {"san": "Nd5#", "text": "Mate. El caballo de c3 llega a d5 y da jaque. El rey no tiene escapatoria."},
                ],
            },
            {
                "type": "move",
                "fen": "rn1qkbnr/ppp2p1p/3p2p1/4N3/2B1P3/2N5/PPPP1PPP/R1BbK2R w KQkq - 0 6",
                "orientation": "white",
                "title": "Ahora dalo tú",
                "text": "Tu dama ha desaparecido. Da mate en 2 con las piezas que te quedan.",
                "line": ["Bxf7+", "Ke7", "Nd5#"],
                "hint": "El alfil de c4 puede tomar f7 con jaque.",
                "success": "¡Mate! Con la dama fuera, el alfil y el caballo bastan: f7 estaba sin defensa.",
            },
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "El mate del loco",
                "text": (
                    "Es el mate más rápido posible: solo dos jugadas blancas. El rey queda expuesto en la diagonal "
                    "e1–h4 en cuanto se mueven f3 y g4."
                ),
                "moves": [
                    {"san": "f3", "text": "Peón a f3: se debilita el rey y la diagonal e1–h4 queda sin peón en f2."},
                    {"san": "e5", "text": "Las negras abren la diagonal de su dama hacia h4."},
                    {"san": "g4", "text": "Otro peón sin motivo. La diagonal e1–h4 sigue abierta y ya no hay nada que la tape."},
                    {"san": "Qh4#", "text": "Mate del loco. La dama da jaque desde h4 y el rey no tiene casillas libres."},
                ],
            },
            {
                "type": "move",
                "fen": "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2",
                "orientation": "black",
                "title": "Dalo tú, con negras",
                "text": "Las blancas acaban de jugar g4. Da el mate en 1 con tu dama.",
                "line": ["Qh4#"],
                "hint": "La dama va a h4 por la diagonal que ha quedado libre.",
                "success": "¡Mate! Con f3 y g4 el rey blanco queda sin escapatoria en la diagonal e1–h4.",
            },
            {
                "type": "select",
                "fen": "rnbqkbnr/pppp1ppp/8/4p3/8/5P2/PPPPP1PP/RNBQKBNR w KQkq - 0 2",
                "orientation": "white",
                "title": "La jugada prohibida",
                "text": "Tras 1.f3 e5 hay una jugada de peón que pierde en el acto. Pulsa la casilla a la que llegaría ese peón.",
                "answer": "g4",
                "wrong": {
                    "g3": "g3 es justo lo contrario: tapa la diagonal e1–h4.",
                    "e3": "e3 deja libre e2 para que el rey escape. No pierde.",
                    "e4": "e4 es una jugada normal: libera e2 y la dama.",
                },
                "success": "Exacto: 2.g4?? permite 2…Dh4#. Con la diagonal e1–h4 abierta, nada puede tapar el jaque.",
            },
        ],
    },
    {
        "id": "sacrificio-h7",
        "course": "aperturas",
        "title": "El sacrificio clásico en h7",
        "summary": "Axh7+, Cg5+ y Dh5: el ataque más famoso contra el enroque. Aprende cuándo funciona y cuándo es un regalo.",
        "minutes": 10,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": GRIEGO,
                "orientation": "white",
                "title": "El regalo griego",
                "text": (
                    "Las condiciones típicas: tu alfil apunta a h7, tu caballo puede saltar a g5, tu dama puede llegar a h5 "
                    "y no hay ningún caballo negro en f6 defendiendo h7 (tu peón de e5 se lo impide). Mira la combinación."
                ),
                "arrows": [["d3", "h7", "green"], ["f3", "g5", "blue"], ["d1", "h5", "blue"]],
                "squares": {"h7": "red", "f6": "yellow"},
                "moves": [
                    {"san": "Bxh7+", "text": "¡Sacrificio! El alfil se come h7 con jaque."},
                    {"san": "Kxh7", "text": "El rey acepta: si no, las blancas han ganado un peón y siguen atacando."},
                    {"san": "Ng5+", "text": "Jaque de caballo. El rey vuelve a g8: en g6 o h6 quedaría aún más expuesto."},
                    {"san": "Kg8", "text": "La retirada más natural."},
                    {"san": "Qd3", "text": "La dama sale hacia h7 (por d3 o por h5, la ruta clásica) y amenaza Dh7 mate. Las negras tendrán que dar material."},
                ],
            },
            {
                "type": "move",
                "fen": GRIEGO,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Lanza el ataque: el sacrificio y el jaque de caballo.",
                "line": ["Bxh7+", "Kxh7", "Ng5+"],
                "hint": "Empieza con el alfil en h7.",
                "success": "¡Perfecto! Stockfish da más de 3 peones de ventaja: la dama llegará a d3 o h5 con amenaza de mate en h7.",
            },
            {
                "type": "choice",
                "fen": GRIEGO_CF6,
                "orientation": "white",
                "title": "¿Funciona aquí?",
                "text": "Tu alfil apunta a h7 y tu caballo está en f3. ¿Juegas Axh7+?",
                "options": [
                    {"text": "Sí, es el sacrificio clásico", "correct": False,
                     "why": "No: el caballo de f6 defiende h7 y recaptura con …Cxh7. Has regalado un alfil. Stockfish: casi 5 peones peor."},
                    {"text": "No: el caballo de f6 defiende h7", "correct": True,
                     "why": "Eso es. Sin un peón en e5 que eche al caballo de f6, el sacrificio no tiene fuerza."},
                ],
            },
            {
                "type": "choice",
                "fen": GRIEGO_SIN_CABALLO,
                "orientation": "white",
                "title": "¿Y aquí?",
                "text": "Es la misma posición del principio, pero tu caballo está en d2 en vez de en f3. ¿Juegas Axh7+?",
                "options": [
                    {"text": "Sí, la dama llega igual a h5", "correct": False,
                     "why": "Sin Cg5+ no hay ataque: el rey negro se queda en h7 tan tranquilo y te falta un alfil. Stockfish: más de 3 peones peor."},
                    {"text": "No: sin el caballo de f3 no hay Cg5+", "correct": True,
                     "why": "Exacto. El caballo que llega a g5 con jaque es la pieza clave. Aquí lo mejor es justamente Cf3, para preparar el sacrificio."},
                ],
            },
        ],
    },
    {
        "id": "rey-centro",
        "course": "aperturas",
        "title": "El rey en el centro",
        "summary": "Un rey sin enrocar está en las líneas por las que viajan damas, alfiles y torres. Castígalo.",
        "minutes": 9,
        "theme": None,
        "steps": [
            {
                "type": "explain",
                "fen": START,
                "orientation": "white",
                "title": "Una trampa para el rey en e1",
                "text": (
                    "La trampa de Blackburne-Shilling: las blancas se comen peones mientras su rey sigue en e1, y la columna e "
                    "se abre. Avanza jugada a jugada."
                ),
                "moves": [
                    {"san": "e4", "text": "Peón al centro."},
                    {"san": "e5", "text": "Las negras igual."},
                    {"san": "Nf3", "text": "Caballo que ataca e5."},
                    {"san": "Nc6", "text": "Las negras lo defienden."},
                    {"san": "Bc4", "text": "El alfil apunta a f7."},
                    {"san": "Nd4", "text": "Un cebo: deja e5 sin defensa."},
                    {"san": "Nxe5", "text": "Las blancas muerden: se comen e5 y amenazan f7."},
                    {"san": "Qg5", "text": "La dama negra ataca e5 y g2."},
                    {"san": "Nxf7", "text": "Las blancas siguen comiendo, con el rey aún en e1."},
                    {"san": "Qxg2", "text": "La dama entra."},
                    {"san": "Rf1", "text": "La torre huye de la dama, pero el rey sigue en el centro."},
                    {"san": "Qxe4+", "text": "¡Jaque por la columna e!"},
                    {"san": "Be2", "text": "Tapa…"},
                    {"san": "Nf3#", "text": "…y mate de la coz: el rey se ha quedado encerrado por sus propias piezas en e1."},
                ],
            },
            {
                "type": "choice",
                "fen": CENTRO_DA4,
                "orientation": "white",
                "title": "Una diagonal abierta",
                "text": "El rey negro sigue en e8 y su alfil de b4 no está protegido. ¿Qué juegas?",
                "arrows": [["a4", "e8", "yellow"]],
                "options": [
                    {"text": "Da4+: jaque y ataque al alfil", "correct": True,
                     "why": "¡Eso es! Con el rey en e8, la diagonal a4-e8 es un arma: jaque y el alfil de b4 cae. Stockfish: la mejor."},
                    {"text": "O-O: ponerte tú a salvo primero", "correct": False,
                     "why": "Aquí no: …Axc3 te destroza los peones. Y además había una pieza gratis con jaque. Stockfish: casi 6 peones de diferencia."},
                    {"text": "Ad2: cambiar alfiles", "correct": False,
                     "why": "Dejas escapar un alfil que podías ganar. Mira las diagonales que llegan al rey de e8."},
                ],
            },
            {
                "type": "move",
                "fen": CENTRO_DA4,
                "orientation": "white",
                "title": "Ahora tú",
                "text": "Castiga al rey de e8. (Lichess, puzzle 3xUtg)",
                "line": ["Qa4+", "c6", "Qxb4"],
                "hint": "La dama da jaque desde a4.",
                "success": "Pieza ganada: el jaque por la diagonal a4-e8 atacó a la vez al alfil de b4.",
            },
            {
                "type": "move",
                "fen": CENTRO_DA5,
                "orientation": "black",
                "title": "Con negras",
                "text": "Ahora el rey sin enrocar es el blanco, en e1. Gana una pieza. (Lichess, puzzle 9T2Zp)",
                "line": ["Qa5+"],
                "hint": "Tu dama puede dar jaque por la diagonal a5-e1.",
                "success": "¡Eso es! Da5+ da jaque al rey de e1 y a la vez ataca el alfil de b5: las blancas tienen que tapar y el alfil cae.",
            },
            {
                "type": "move",
                "fen": CENTRO_HORQ,
                "orientation": "white",
                "title": "Cambia y remata",
                "text": "Las damas se miran y el rey negro sigue en e8. Cambia damas… y la horquilla hará el resto. (Lichess, puzzle 2dxx2)",
                "line": ["Qxd8+", "Kxd8", "Nxf7+"],
                "hint": "Primero cambia las damas con jaque.",
                "success": "¡Horquilla! El rey tuvo que recapturar en d8 y Cxf7+ ataca a la vez al rey y a la torre de h8.",
            },
        ],
    },
]
