import os
import logging
import time
from fastapi import FastAPI, status, Response, Request
from curl_cffi import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from pydantic import BaseModel
import pendulum

# noinspection PyPackageRequirements
from dotenv import load_dotenv

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
cache_timestamp = {"rss": 0, "atom": 0}

app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


def generate_rss(request: Request, atom=False):
    logger.info("Requesting Bandcamp feed")
    response = requests.get(URL, cookies=COOKIES, impersonate="chrome", timeout=30)
    response.raise_for_status()
    logger.info("Received response from Bandcamp")

    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all("li", class_="story nr")
    logger.debug(f"Found {len(items)} items in the feed")

    fg = FeedGenerator()
    fg.title("Bandcamp User Feed")
    fg.id(URL)
    fg.link(href=URL)
    fg.link(href=str(request.url), rel="self")
    fg.description("RSS feed of my Bandcamp news feed")

    for item in items:
        title = item.find("div", class_="collection-item-title").text.strip()
        id_ = item.attrs.get("data-story-tralbum-key")
        artist = item.find("a", class_="artist-name").text.strip()
        album_link = item.find("a", class_="item-link")["href"]
        cover_image = item.find("img", class_="tralbum-art-large")["src"]
        release_date = item.find("div", class_="story-date").text.strip()
        description = item.find("div", class_="collection-item-artist").text.strip()
        tags = ", ".join(a.text.strip() for a in item.find("div", class_="collection-item-tags").find_all("a"))

        entry = fg.add_entry()
        entry.id(f"{album_link}#{id_}")
        entry.title(f"{title} by {artist}")
        entry.link(href=album_link)
        entry.description(f"{description} - {tags}")

        if release_date.lower() == "yesterday":
            pub_date = pendulum.now().subtract(days=1)
        else:
            try:
                pub_date = pendulum.from_format(release_date, "MMM D, YYYY")
            except ValueError:
                logger.warning(f"Unexpected date format for release_date: {release_date}")
                pub_date = pendulum.now()

        entry.pubDate(pub_date)
        entry.enclosure(url=cover_image, type="image/jpeg")

    logger.info("RSS feed generated successfully")
    return fg.rss_str(pretty=True) if not atom else fg.atom_str(pretty=True)


async def _rss_feed(request: Request, atom=False):
    feed_type = "atom" if atom else "rss"
    current_time = time.time()

    # Check cache validity
    if cache[feed_type] and (current_time - cache_timestamp[feed_type]) < CACHE_DURATION_SECONDS:
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
    response_model=HealthCheck,
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
    logger.info("Health check endpoint accessed")
    return HealthCheck(status="OK")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
