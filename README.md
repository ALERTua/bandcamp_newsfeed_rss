[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

Bandcamp Newsfeed RSS Feed Generator
---------------------------

FastAPI RSS Feed Generator for your Bandcamp newsfeed

Makes RSS feed out of your https://bandcamp.com/{BANDCAMP_USERNAME}/feed,
so you can follow the new releases using your favorite RSS reader

Bandcamp Feed vs Generated RSS
![](media/screenshot_1.png)

.env:
```
PORT=8000
BANDCAMP_USERNAME=my_bandcamp_username
# "identity" cookie
IDENTITY=7%09ABCV1A%2B12D12D12ABCDEJbOCvA8Mfi90betEmFcYfhs%3D%09%7B%22id%22%3A135750916%2C%22ex%22%3A0%7D
CACHE_DURATION_SECONDS=3600
```
serves:
- /rss
- /atom
- /health
