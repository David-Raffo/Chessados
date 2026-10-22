"""Lecciones de finales teóricos. Cada posición está comprobada con Stockfish (profundidad 30).

goal:
  mate  → hay que dar jaque mate.
  win   → mate, o dejar al rival con el rey solo mientras conservas dama o torre a salvo.
  draw  → conseguir tablas por reglamento o aguantar `moves` jugadas sin quedar perdido.
"""

LESSONS = [
    # --- Mates básicos ---
    {
        "id": "mate-dos-torres", "level": "Mates básicos", "title": "Mate con dos torres", "rating": 600,
        "fen": "8/8/3k4/8/8/8/8/R3K2R w - - 0 1", "color": "white", "goal": "mate", "moves": 20,
        "tip": "La escalera: una torre corta una fila y la otra da jaque en la siguiente. Si el rey ataca una torre, llévala al otro extremo.",
    },
    {
        "id": "mate-dama", "level": "Mates básicos", "title": "Mate de dama", "rating": 750,
        "fen": "8/8/8/4k3/8/8/8/3QK3 w - - 0 1", "color": "white", "goal": "mate", "moves": 25,
        "tip": "Encierra al rey con la dama a un salto de caballo, empújalo al borde y acerca tu rey. Cuidado con el ahogado.",
    },
    {
        "id": "mate-torre", "level": "Mates básicos", "title": "Mate de torre", "rating": 950,
        "fen": "8/8/8/4k3/8/8/8/4K2R w - - 0 1", "color": "white", "goal": "mate", "moves": 35,
        "tip": "Reduce la caja del rey con la torre y usa tu rey en oposición para empujarlo hacia el borde.",
    },
    {
        "id": "mate-dos-alfiles", "level": "Mates básicos", "title": "Mate con dos alfiles", "rating": 1500,
        "fen": "8/8/8/4k3/8/8/8/2B1KB2 w - - 0 1", "color": "white", "goal": "mate", "moves": 45,
        "tip": "Los alfiles juntos forman una barrera diagonal. Lleva al rey a una esquina, cualquiera sirve.",
    },
    {
        "id": "mate-alfil-caballo", "level": "Mates básicos", "title": "Mate de alfil y caballo", "rating": 2200,
        "fen": "8/8/8/4k3/8/8/8/1N2KB2 w - - 0 1", "color": "white", "goal": "mate", "moves": 50,
        "tip": "Solo se da mate en la esquina del color de tu alfil. Usa la maniobra en W del caballo para llevar al rey allí.",
    },
    # --- Rey y peón ---
    {
        "id": "rp-sexta", "level": "Rey y peón", "title": "El rey delante, en sexta", "rating": 900,
        "fen": "4k3/8/4K3/4P3/8/8/8/8 w - - 0 1", "color": "white", "goal": "win", "moves": 20,
        "tip": "Con tu rey en sexta delante del peón la victoria es segura, mueva quien mueva. Avanza el peón cuando tu rey controle la casilla de delante.",
    },
    {
        "id": "rp-oposicion", "level": "Rey y peón", "title": "Ganar la oposición", "rating": 1150,
        "fen": "8/8/8/4k3/8/4K3/4P3/8 b - - 0 1", "color": "white", "goal": "win", "moves": 25,
        "tip": "Mueven las negras. Mantén a tu rey delante del peón y toma la oposición: reyes enfrentados con una casilla entre medias y le toca mover al rival.",
    },
    {
        "id": "rp-cuadrado", "level": "Rey y peón", "title": "La regla del cuadrado", "rating": 800,
        "fen": "8/8/8/4k3/P7/8/8/7K b - - 0 1", "color": "black", "goal": "draw", "moves": 12,
        "tip": "Dibuja el cuadrado desde el peón hasta la casilla de coronación. Si tu rey entra en él, lo alcanzas.",
    },
    {
        "id": "rp-defensa", "level": "Rey y peón", "title": "Defender con la oposición", "rating": 1100,
        "fen": "8/8/8/4k3/8/4K3/4P3/8 w - - 0 1", "color": "black", "goal": "draw", "moves": 20,
        "tip": "Juegas con negras y tienes la oposición. Quédate delante del peón y responde a cada movimiento del rey blanco enfrentándolo.",
    },
    {
        "id": "rp-defensa-final", "level": "Rey y peón", "title": "Bloquear el peón", "rating": 1250,
        "fen": "4k3/8/8/4K3/4P3/8/8/8 b - - 0 1", "color": "black", "goal": "draw", "moves": 20,
        "tip": "Retrocede en línea recta delante del peón. Cuando el peón dé jaque en séptima, ve a la casilla de delante y llegará el ahogado o la oposición.",
    },
    {
        "id": "rp-torre", "level": "Rey y peón", "title": "El peón de torre", "rating": 950,
        "fen": "7k/8/8/6KP/8/8/8/8 b - - 0 1", "color": "black", "goal": "draw", "moves": 15,
        "tip": "Si tu rey llega a la esquina de coronación del peón de torre, no hay forma de sacarlo: son tablas.",
    },
    # --- Torres y damas ---
    {
        "id": "torre-lucena", "level": "Torres y damas", "title": "Posición de Lucena", "rating": 1750,
        "fen": "1K6/1P1k4/8/8/8/8/r7/2R5 w - - 0 1", "color": "white", "goal": "win", "moves": 30,
        "tip": "Corta al rey enemigo y «construye el puente»: lleva tu torre a la cuarta fila para tapar los jaques laterales.",
    },
    {
        "id": "torre-philidor", "level": "Torres y damas", "title": "Posición de Philidor", "rating": 1650,
        "fen": "4k3/8/7r/4K3/4P3/8/8/R7 b - - 0 1", "color": "black", "goal": "draw", "moves": 25,
        "tip": "Torre en tu tercera fila hasta que el peón avance; entonces llévala a la primera y da jaques por detrás.",
    },
    {
        "id": "dama-peon", "level": "Torres y damas", "title": "Dama contra peón en séptima", "rating": 1400,
        "fen": "Q7/8/8/8/8/8/3pk3/7K w - - 0 1", "color": "white", "goal": "win", "moves": 30,
        "tip": "Con jaques y clavadas obliga al rey a colocarse delante del peón; cada vez que lo hace, acerca tu rey un paso.",
    },
]

BY_ID = {lesson["id"]: lesson for lesson in LESSONS}
