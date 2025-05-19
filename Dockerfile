FROM python:3.13

WORKDIR /app

RUN apt update && apt install curl

RUN apt clean

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PYTHONPATH: /app:$PYTHONPATH
ENV PATH="/root/.local/bin:${PATH}"

COPY ./uv.lock .
COPY ./pyproject.toml .

RUN uv sync
