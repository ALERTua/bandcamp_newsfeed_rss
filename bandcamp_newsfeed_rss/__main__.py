"""Main entry point for the Bandcamp RSS feed service."""

import os

import uvicorn

from .app import create_app

app = create_app()
port = int(os.getenv("PORT", "8000"))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
