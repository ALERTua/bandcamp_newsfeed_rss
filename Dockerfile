ARG PYTHON_VERSION=3.13

ARG SOURCE_DIR_NAME=bandcamp_newsfeed_rss

ARG APP_DIR=/app
ARG UV_PROJECT_ENVIRONMENT=.venv
ARG UV_CACHE_DIR=.uv_cache


FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-alpine AS builder

ARG UV_CACHE_DIR
ARG UV_PROJECT_ENVIRONMENT
ARG APP_DIR

ENV \
    # uv
    UV_PYTHON_DOWNLOADS=0 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    UV_NO_PROGRESS=true \
    UV_CACHE_DIR=$UV_CACHE_DIR \
    UV_PROJECT_ENVIRONMENT=$UV_PROJECT_ENVIRONMENT \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # App
    APP_DIR=$APP_DIR

WORKDIR $APP_DIR

RUN \
    --mount=type=cache,target=$UV_CACHE_DIR \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev


FROM builder AS production

LABEL maintainer="ALERT <alexey.rubasheff@gmail.com>"

ARG SOURCE_DIR_NAME

ARG APP_DIR
ARG UV_PROJECT_ENVIRONMENT
ARG UV_CACHE_DIR

ENV \
    # OS
    UID=1000 \
    GID=1000 \
    USER=appuser \
    GROUP=appgroup \
    # App
    APP_DIR=$APP_DIR \
    SOURCE_DIR_NAME=$SOURCE_DIR_NAME \
    PORT=8000 \
    BANDCAMP_USERNAME="" \
    IDENTITY="" \
    TZ="Europe/London" \
    CACHE_DURATION_SECONDS=3600 \
    # uv
    UV_PROJECT_ENVIRONMENT=$UV_PROJECT_ENVIRONMENT \
    UV_CACHE_DIR=$UV_CACHE_DIR \
    # Python
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8


EXPOSE $PORT

WORKDIR $APP_DIR

RUN \
    addgroup --gid $GID "$GROUP" \
    && adduser --no-create-home --disabled-password \
    --ingroup "$GROUP" --uid "$UID" $USER \
    && chown $UID:$GID $APP_DIR

COPY \
    --from=builder \
    --chown=$UID:$GID \
    $APP_DIR/$UV_PROJECT_ENVIRONMENT $UV_PROJECT_ENVIRONMENT

COPY \
    --chown=$UID:$GID \
    $SOURCE_DIR_NAME $SOURCE_DIR_NAME

USER $USER

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
        CMD curl localhost:${PORT}/health || exit 1

ENTRYPOINT []

CMD uv run uvicorn $SOURCE_DIR_NAME.__main__:app --host 0.0.0.0 --port ${PORT-8000}
#CMD /bin/sh
