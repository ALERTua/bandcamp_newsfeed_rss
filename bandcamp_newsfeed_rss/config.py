"""Application configuration."""

import logging
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

# Required settings
BANDCAMP_USERNAME = os.getenv("BANDCAMP_USERNAME")
assert BANDCAMP_USERNAME, "BANDCAMP_USERNAME environment variable not set"
IDENTITY = os.getenv("IDENTITY")
assert IDENTITY, "IDENTITY environment variable not set"

# Optional settings with defaults
VERBOSE = os.getenv("VERBOSE", "0")
log_level = logging.DEBUG if VERBOSE == "1" else logging.INFO

CACHE_DURATION_SECONDS = int(os.getenv("CACHE_DURATION_SECONDS", "3600"))
TZ = os.getenv("TZ", "Europe/London")
TIMEZONE = ZoneInfo(TZ)

# Logging setup
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.info(f"Logging level set to {'DEBUG' if log_level == logging.DEBUG else 'INFO'}")
