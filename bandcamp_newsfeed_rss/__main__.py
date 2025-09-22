import logging
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import curl_cffi as cc
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from fastapi import FastAPI, status, Response, Request
from feedgen.feed import FeedGenerator
from pydantic import BaseModel

load_dotenv()

BANDCAMP_USERNAME = os.getenv("BANDCAMP_USERNAME")
assert BANDCAMP_USERNAME, "BANDCAMP_USERNAME environment variable not set"
IDENTITY = os.getenv("IDENTITY")
assert IDENTITY, "IDENTITY environment variable not set"

URL = f"https://bandcamp.com/{BANDCAMP_USERNAME}/feed"
COOKIES = {"identity": IDENTITY}

VERBOSE = os.getenv("VERBOSE", "0")
log_level = logging.DEBUG if VERBOSE == "1" else logging.INFO

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.info(f"Logging level set to {'DEBUG' if log_level == logging.DEBUG else 'INFO'}")

# Cache configuration
# Cache duration in seconds (default 60 minutes)
CACHE_DURATION_SECONDS = int(os.getenv("CACHE_DURATION_SECONDS", "3600"))
cache = {"rss": None, "atom": None}
cache_timestamp = {"rss": 0.0, "atom": 0.0}

TZ = os.getenv("TZ", "Europe/London")
TIMEZONE = ZoneInfo(TZ)

app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


def generate_rss(request: Request, atom=False):
    logger.info("Requesting Bandcamp feed")
    response = cc.get(URL, cookies=COOKIES, impersonate="chrome", timeout=30)
    response.raise_for_status()
    logger.info("Received response from Bandcamp")

    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all("li", class_="story nr")
    items = items[::-1]  # Reverse the order of items
    logger.debug(f"Found {len(items)} items in the feed")

    fg = FeedGenerator()
    fg.title(f"Bandcamp {BANDCAMP_USERNAME} Feed")
    fg.id(URL)
    fg.link(href=URL)
    fg.link(href=str(request.url), rel="self")
    fg.description(f"RSS feed of {BANDCAMP_USERNAME} Bandcamp news feed")

    for item in items:
        title = item.find("div", class_="collection-item-title").text.strip()
        id_ = item.attrs.get("data-story-tralbum-key")
        artist = item.find("a", class_="artist-name").text.strip()
        album_link = item.find("a", class_="item-link")["href"]
        cover_image = item.find("img", class_="tralbum-art-large")["src"]
        release_date = item.find("div", class_="story-date").text.strip()

        entry = fg.add_entry()
        entry.id(f"{album_link}#{id_}")
        entry.title(f"{title} by {artist}")
        entry.link(href=album_link)
        entry.author({"name": artist})
        # Process HTML: remove tralbum-owners div and wrap in container
        item_copy = BeautifulSoup(str(item), "html.parser")

        remove_elements_classes = [
            ("div", "tralbum-owners"),
            ("div", "story-sidebar"),
            ("div", "tralbum-wrapper-collect-controls"),
            ("span", "track_play_time"),
        ]
        for div_type, div_class in remove_elements_classes:
            div_to_remove = item_copy.find(div_type, class_=div_class)
            if div_to_remove:
                div_to_remove.decompose()

        html_content = f'<div class="collection-item-container">{item_copy}</div>'

        entry.description(html_content)

        if release_date.lower() == "yesterday":
            pub_date = datetime.now(tz=TIMEZONE) - timedelta(days=1)
        else:
            try:
                pub_date = datetime.strptime(release_date, "%b %d, %Y").replace(tzinfo=TIMEZONE)
            except ValueError:
                logger.warning(f"Unexpected date format for release_date: {release_date}")
                pub_date = datetime.now(tz=TIMEZONE)

        entry.pubDate(pub_date)
        entry.enclosure(url=cover_image, type="image/jpeg")

    logger.info("RSS feed generated successfully")
    return fg.rss_str(pretty=True) if not atom else fg.atom_str(pretty=True)


async def _rss_feed(request: Request, atom=False):
    feed_type = "atom" if atom else "rss"
    current_time = time.time()

    # Check cache validity
    if cache.get(feed_type) and (current_time - cache_timestamp.get(feed_type, 0)) < CACHE_DURATION_SECONDS:
        logger.info(f"Returning cached {feed_type} feed")
        return Response(content=cache[feed_type], media_type="application/xml", status_code=status.HTTP_200_OK)

    rss_content = generate_rss(request, atom=atom)
    cache[feed_type] = rss_content
    cache_timestamp[feed_type] = current_time
    logger.info(f"Generated new {feed_type} feed and updated cache")

    # TODO: consider
    # TODO: media_type = "application/atom+xml" if atom else "application/rss+xml"
    # TODO: return Response(content=rss_content, media_type=media_type, status_code=status.HTTP_200_OK)

    return Response(content=rss_content, media_type="application/xml", status_code=status.HTTP_200_OK)


@app.get("/rss", response_class=Response)
async def rss_feed(request: Request):
    """Endpoint to generate and return the RSS feed."""
    return await _rss_feed(request, atom=False)


@app.get("/atom", response_class=Response)
async def atom_feed(request: Request):
    """Endpoint to generate and return the RSS feed."""
    return await _rss_feed(request, atom=True)


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).

    Returns
    -------
        HealthCheck: Returns a JSON response with the health status

    """
    logger.debug("Health check endpoint accessed")
    return HealthCheck(status="OK")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), log_level="info")
