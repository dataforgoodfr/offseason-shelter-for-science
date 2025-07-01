FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY . /app

WORKDIR /app

RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN uv sync --frozen --no-cache --no-dev

CMD ["uv", "run", "fastapi", "run", "rescue_api/main.py", "--port", "80"]
