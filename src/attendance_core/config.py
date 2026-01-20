from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
LOGS_FILE = DATA_DIR / "logs.json"
USERS_FILE = DATA_DIR / "users.json"