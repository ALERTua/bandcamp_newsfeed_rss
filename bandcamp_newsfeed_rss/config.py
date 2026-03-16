"""Application configuration."""

import logging
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

# Required settings
BANDCAMP_USERNAME = os.getenv("BANDCAMP_USERNAME") or os.getenv("TEST_BANDCAMP_USERNAME")
IDENTITY = os.getenv("IDENTITY") or os.getenv("TEST_IDENTITY")

# Allow tests to run without real credentials
if os.getenv("TESTING"):
    BANDCAMP_USERNAME = BANDCAMP_USERNAME or "test_user"
    IDENTITY = IDENTITY or "test_identity"
else:
    assert BANDCAMP_USERNAME, "BANDCAMP_USERNAME environment variable not set"
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
