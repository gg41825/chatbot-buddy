import os
from pathlib import Path

# ========== Load .env file ==========
try:
    from dotenv import load_dotenv
    
    # .env file location
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        if int(os.getenv("DEV_MODE", "0")):
            print(f"[Config] Loaded .env from: {env_path}")
    else:
        print(f"[Config] .env not found at {env_path}")
        print(f"[Config] Using environment variables or default values")
        
except ImportError:
    print("[Config] python-dotenv not installed")
    print("[Config] Using environment variables only")
    print("[Config] Install with: pip install python-dotenv")

# app
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", 8080))
APP_ANALYZER_KEY = os.getenv("APP_ANALYZER_KEY")

# news
NEWS_SCRAPER_TYPE = os.getenv("NEWS_SCRAPER_TYPE")
NEWS_REQUEST_URL = os.getenv("NEWS_REQUEST_URL")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# mysql
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DBNAME = os.getenv("MYSQL_DBNAME")

# openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_LANG_MODEL = os.getenv("OPENAI_LANG_MODEL")