import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
for env_name in ["sai.env", "yash.env", ".env"]:
    env_path = Path(__file__).resolve().parent.parent / env_name
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break
else:
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Credentials
WQ_EMAIL = os.getenv("WQ_EMAIL", "")
WQ_PASSWORD = os.getenv("WQ_PASSWORD", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# API Endpoints
WQ_AUTH_URL = "https://api.worldquantbrain.com/authentication"
WQ_SIM_URL = "https://api.worldquantbrain.com/simulations"
WQ_ALPHAS_URL = "https://api.worldquantbrain.com/alphas"

# Database Configuration
DB_DIR = Path("/data")
try:
    DB_DIR.mkdir(exist_ok=True)
except (PermissionError, OSError):
    DB_DIR = BASE_DIR / "db"
    DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "alpha_vault.db"

# Alphas Output Directory
ALPHAS_OUT_DIR = BASE_DIR / "alphas"
ALPHAS_OUT_DIR.mkdir(exist_ok=True)

# Simulation Default Parameters
DEFAULT_SIM_SETTINGS = {
    "nanHandling": "OFF",
    "instrumentType": "EQUITY",
    "delay": 1,
    "universe": "TOP3000",
    "truncation": 0.1,
    "unitHandling": "VERIFY",
    "pasteurization": "ON",
    "region": "USA",
    "language": "FASTEXPR",
    "decay": 6,
    "neutralization": "SUBINDUSTRY",
    "visualization": False
}

# Decision Thresholds
SHARPE_THRESHOLD_PASS = 1.25
SHARPE_THRESHOLD_RETRY = 1.0
FITNESS_THRESHOLD = 1.0
MIN_TURNOVER = 1.0  # %
MAX_TURNOVER = 70.0  # %

# Log Streaming Server Settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

# Concurrency settings
# Increased to 8 for Gold/Consultant tier account, can be overridden via environment variables
MAX_CONCURRENT_SIMS = int(os.getenv("MAX_CONCURRENT_SIMS", "8"))
