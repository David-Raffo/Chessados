import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://chess:chess@localhost:5432/chess")
DEFAULT_JWT_SECRET = "cambia-este-secreto"  # valor de ejemplo: nunca se usa para firmar
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_DAYS = int(os.getenv("JWT_DAYS", "30"))

STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")
ANALYSIS_DEPTH = int(os.getenv("ANALYSIS_DEPTH", "18"))
QUICK_DEPTH = int(os.getenv("QUICK_DEPTH", "10"))  # primera pasada, para ver el análisis en segundos
ANALYSIS_THREADS = int(os.getenv("ANALYSIS_THREADS", "2"))

MAIA_URL = os.getenv("MAIA_URL", "http://maia:8001")

PUZZLE_URL = os.getenv("PUZZLE_URL", "https://database.lichess.org/lichess_db_puzzle.csv.zst")
PUZZLE_FILE = os.getenv("PUZZLE_FILE", "/data/lichess_db_puzzle.csv.zst")
PUZZLE_LIMIT = int(os.getenv("PUZZLE_LIMIT", "1000000"))  # 0 = todos
PUZZLE_MIN_POPULARITY = int(os.getenv("PUZZLE_MIN_POPULARITY", "80"))
PUZZLE_MIN_PLAYS = int(os.getenv("PUZZLE_MIN_PLAYS", "300"))

# Áreas de tiempo (reparto objetivo) y áreas con ELO propio
TIME_AREAS = ["tactics", "play", "endgames", "openings"]
RATING_AREAS = ["play", "tactics", "endgames", "rush"]
DEFAULT_SPLIT = {"tactics": 40, "play": 35, "endgames": 15, "openings": 10}
