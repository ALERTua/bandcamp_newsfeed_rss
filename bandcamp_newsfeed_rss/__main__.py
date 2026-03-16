"""Main entry point for the Bandcamp RSS feed service."""

import os

import uvicorn

from .app import create_feed_app


def main() -> None:
    """Run the application."""
    app = create_feed_app()
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
