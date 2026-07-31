import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Automatically load environment variables from .env file if present
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
else:
    load_dotenv()

# Render /var/data persistent storage or local directory
if os.path.exists("/var/data"):
    DATABASE_PATH = Path("/var/data/crm_database.db")
else:
    DATABASE_PATH = BASE_DIR / "crm_database.db"

INVOICES_DIR = BASE_DIR / "invoices_pdf"

# Ensure invoices directory exists
INVOICES_DIR.mkdir(exist_ok=True)

SECRET_KEY = os.environ.get("SECRET_KEY", "bizflow-ai-crm-secret-key-2026-fixed-token")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
