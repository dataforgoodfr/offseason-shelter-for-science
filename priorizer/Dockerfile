FROM ghcr.io/astral-sh/uv:python3.9-alpine

COPY . /app

WORKDIR /app

RUN uv sync --frozen --no-cache --no-dev
RUN apk add --no-cache --virtual .build-deps curl

EXPOSE 8082

CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8082"]