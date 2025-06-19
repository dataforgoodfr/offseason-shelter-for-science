# Rescue DB

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)


## Description

This folder contains the backend app to manage and interact with the rescue list database. In brief, it contains the list of different datasets and corresponding metadata to rescue.

## Run locally

### Requirements

- [uv](https://docs.astral.sh/uv/) for python packaging and install
- [Docker Compose](https://docs.docker.com/compose/) to run locally

### Running the app

First, copy the `.env.dist` to a `.env` file and fill in the different variables:

```sh
cp .env.dist .env
```

Then, to run the backend and db :

```sh
docker compose build # if any changes in the backend code
docker compose up
```

You can also run the backend locally:

```sh
uv run fastapi dev rescue_api/main.py
```

> In dev mode, changes are applied directly

Then you should be able to see the API docs at http://127.0.0.1:8000/docs

## Development

### DB migrations

Migrations on the db are performed using [alembic](https://alembic.sqlalchemy.org/en/latest/index.html).

To make sure you have the database with the most recent changes:

```sh
uv run alembic upgrade head
```

#### Create new migrations

Once you have made changes in the `rescue_api/models/` directory, by adding a new model or modifying an existing one you can run the following to generate a template for your migration.

```sh
uv run alembic revision --autogenerate -m "Comment about my modifications"
```

Then your migration file is created in the `alembic/versions/` directory. You can edit this file and make sure the migration is correct.
