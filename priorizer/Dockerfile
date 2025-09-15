FROM ghcr.io/astral-sh/uv:python3.9-alpine

COPY . /app

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps curl git
RUN uv sync --frozen --no-cache --no-dev

EXPOSE 8082

CMD ["uv", "run", "fastapi", "run", "api/priorizer_service.py", "--host", "0.0.0.0", "--port", "8082"]