import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = "8118589511:AAFHleVFkF-3kiLtpyxxSUfOxdsuMkoak48"

# Database Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = "apple_tv_keys"
KEYS_COLLECTION = "keys"

# Browser Configuration
HEADLESS = True
MAX_BROWSERS = 3
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
]

# URLs
REDEEM_URL = "https://redeem.services.apple/card-apple-entertainment-offer-1-2025"
BUTTON_XPATH = "/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[1]/div/div[2]/button"

# Key Generation Settings
DEFAULT_KEYS_TO_GENERATE = 5
MAX_KEYS_PER_REQUEST = 20
KEY_GENERATION_INTERVAL = 60  # seconds 