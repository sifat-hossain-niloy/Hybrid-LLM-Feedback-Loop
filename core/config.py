import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./icpc.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
PLAYWRIGHT_STORAGE = os.getenv("PLAYWRIGHT_STORAGE","infra/playwright/storageState.json")
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS","3"))
CF_SUBMIT_SPACING_SEC = int(os.getenv("CF_SUBMIT_SPACING_SEC","10"))
CF_POLL_TIMEOUT_SEC = int(os.getenv("CF_POLL_TIMEOUT_SEC","900"))
CF_DEFAULT_LANG_ID = int(os.getenv("CF_DEFAULT_LANG_ID","54"))

# Codeforces authentication
CF_USERNAME = os.getenv("CF_USERNAME")
CF_PASSWORD = os.getenv("CF_PASSWORD")

# CAPTCHA solving service (optional)
CAPTCHA_SERVICE = os.getenv("CAPTCHA_SERVICE", "none")  # "2captcha", "anticaptcha", "none"
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY")

# Submission method preference
CF_SUBMIT_METHOD = os.getenv("CF_SUBMIT_METHOD", "cloudscraper")  # "cloudscraper", "playwright"
