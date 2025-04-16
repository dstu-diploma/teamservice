from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise
from fastapi import FastAPI
from os import environ


def get_tortoise_url() -> str:
    url: str | None = environ.get("DATABASE_URL")

    if url is None:
        raise KeyError(
            "Необходимо указать DATABASE_URL в переменных окружения!"
        )

    return url


TORTOISE_ORM = {
    "connections": {"default": get_tortoise_url()},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI):
    Tortoise.init_models(["app.models"], "models")
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        modules={"models": ["app.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )
