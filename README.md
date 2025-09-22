[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

Bandcamp Newsfeed RSS Feed Generator
---------------------------

FastAPI RSS Feed Generator for your Bandcamp newsfeed

Makes RSS feed out of your https://bandcamp.com/{BANDCAMP_USERNAME}/feed,
so you can follow the new releases using your favorite RSS reader

![](media/screenshot_1.png)

## Usage

1. Get your Bandcamp identity cookie from browser dev tools (Network tab when loading your feed page)
2. Create `.env` file with required variables (described below)
3. Run locally or deploy using one of the methods described below

## Configuration

* Create `.env` file using [.env.example](.env.example)
```
BANDCAMP_USERNAME=my_bandcamp_username
# "identity" cookie from Bandcamp (required for private feeds)
IDENTITY=7%09ABCV1A%2B12D12D12ABCDEJbOCvA8Mfi90betEmFcYfhs%3D%09%7B%22id%22%3A135750916%2C%22ex%22%3A0%7D
PORT=8000
CACHE_DURATION_SECONDS=3600
TZ=Europe/Kiev
VERBOSE=0
```

## Running locally

* Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
* Pre-create `.env` using [.env.example](.env.example)
* Run the project
```bash
uv run bandcamp_newsfeed_rss
```
* Open http://127.0.0.1:8000/rss in the browser.
Other endpoints are described below

## Docker Deployment

### Building the image and running the container
```bash
# Build the image
docker build -t bandcamp_newsfeed_rss .

# Run the container using .env file
docker run -p 8000:8000 --env-file .env bandcamp_newsfeed_rss

# Or run the container using the environment variable arguments
docker run -p 8000:8000 \
  -e BANDCAMP_USERNAME=your_username \
  -e IDENTITY=your_identity_cookie \
  -e TZ=Europe/Kiev \
  bandcamp_newsfeed_rss
```

### Using the pre-built image
```bash
# Run the container using .env file
docker run -p 8000:8000 --env-file .env ghcr.io/alertua/bandcamp_newsfeed_rss

# Or run the container using the environment variable arguments
docker run -p 8000:8000 \
  -e BANDCAMP_USERNAME=your_username \
  -e IDENTITY=your_identity_cookie \
  -e TZ=Europe/Kiev \
  ghcr.io/alertua/bandcamp_newsfeed_rss
```

## Endpoints

- `/rss` - RSS 2.0 feed
- `/atom` - Atom feed
- `/health` - Health check
