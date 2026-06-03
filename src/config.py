import os
from pathlib import Path
# Load environment variables (optional/conditional to avoid crashes on Render where env vars are set via Dashboard)
try:
    from dotenv import load_dotenv
    for env_name in ["sai.env", "yash.env", ".env"]:
        env_path = Path(__file__).resolve().parent.parent / env_name
        if env_path.exists():
            load_dotenv(env_path, override=True)
            break
    else:
        load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Credentials
WQ_EMAIL = os.getenv("WQ_EMAIL", "")
WQ_PASSWORD = os.getenv("WQ_PASSWORD", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Yash Thakre OPI (Slots 1-4)
OPI_EMAIL = os.getenv("OPI_EMAIL", "saineela731@gmail.com")
OPI_PASSWORD = os.getenv("OPI_PASSWORD", "iitg@123")
OPI_API_TOKEN = os.getenv("OPI_API_TOKEN", "yashthakreop")
GROUPA_API_TOKEN = OPI_API_TOKEN

# Yash Thakre OPI Pro (Slots 5-8)
OPI_PRO_EMAIL = os.getenv("OPI_PRO_EMAIL", "beyondsynapse@gmail.com")
OPI_PRO_PASSWORD = os.getenv("OPI_PRO_PASSWORD", "Web3@ytop")
OPI_PRO_API_TOKEN = os.getenv("OPI_PRO_API_TOKEN", "yashthakrepro")
GROUPB_API_TOKEN = OPI_PRO_API_TOKEN



# API Endpoints
WQ_AUTH_URL = "https://api.worldquantbrain.com/authentication"
WQ_SIM_URL = "https://api.worldquantbrain.com/simulations"

WQ_ALPHAS_URL = "https://api.worldquantbrain.com/alphas"

# Database Configuration
DB_DIR = Path("/data")
try:
    DB_DIR.mkdir(exist_ok=True)
    # Test writability of the directory
    test_file = DB_DIR / ".write_test"
    test_file.touch()
    test_file.unlink()
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
# Set to 3 to align with standard WQ account cap of 3 slots (3 batches of 10 = 30 concurrent alphas)
MAX_CONCURRENT_SIMS = int(os.getenv("MAX_CONCURRENT_SIMS", "3"))
