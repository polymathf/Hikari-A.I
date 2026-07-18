import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
PARSE_MODE = "HTML"


def _load_api_keys() -> list[str]:
    """Load one or more comma-separated API keys from the environment."""
    raw_keys = os.getenv("DEEPSEEK_API_KEYS") or os.getenv("DEEPSEEK_API_KEY", "")
    return [key.strip() for key in raw_keys.split(",") if key.strip()]


DEEPSEEK_API_KEYS = _load_api_keys()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

PROMPT_STYLES = {
    "default": {
        "files": {
            "eng": "prompt_eng.txt",
            "rus": "prompt_rus.txt",
            "chi": "promt_chi.txt",
            "ukr": "promt_ukr.txt",
            "kaz": "promt_kaz.txt",
        }
    },
    "cute": {
        "files": {
            "eng": "cute_prompt_eng.txt",
            "rus": "cute_prompt_rus.txt",
            "chi": "cute_prompt_chi.txt",
            "ukr": "cute_prompt_ukr.txt",
            "kaz": "cute_prompt_kaz.txt",
        }
    },
    "cheeky": {
        "files": {
            "eng": "cheeky_prompt_eng.txt",
            "rus": "cheeky_prompt_rus.txt",
            "chi": "cheeky_prompt_chi.txt",
            "ukr": "cheeky_prompt_ukr.txt",
            "kaz": "cheeky_prompt_kaz.txt",
        }
    },
}
