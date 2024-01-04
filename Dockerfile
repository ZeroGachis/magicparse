FROM python:3.10-slim-bullseye

RUN apt update && apt install -y git

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VENV=/opt/poetry \
    POETRY_VERSION=1.7.1 \
    APP_DIR=/home/src/magicparse

# Add poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

WORKDIR $APP_DIR

# Activate the app virtualenv
ENV APP_VENV="$APP_DIR/.venv"
ENV PATH="$APP_VENV/bin:$PATH"
RUN python3 -m venv $APP_VENV

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . ./

RUN poetry install

CMD ["bash"]
