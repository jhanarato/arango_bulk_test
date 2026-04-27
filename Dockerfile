FROM python:3.6.2

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

RUN uv sync

ENTRYPOINT ["uv", "run", "pytest"]