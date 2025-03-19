"""Initialize environment variables for the dataset module."""

import os

from dotenv import load_dotenv

load_dotenv()

PURPLE_PROTOCOL: str = os.getenv("PURPLE_PROTOCOL", "http")
PURPLE_PORT: int = int(os.getenv("PURPLE_PORT", "8001"))
PURPLE_HOST: str = os.getenv("PURPLE_HOST", "localhost")
PURPLE_DEBUG: str = os.getenv("PURPLE_DEBUG", "FALSE")

APP_URL = f"{PURPLE_PROTOCOL}://{PURPLE_HOST}:{PURPLE_PORT}"
