from tortoise.contrib.fastapi import register_tortoise
from app.config import Settings
from tortoise import Tortoise
from fastapi import FastAPI


TORTOISE_ORM = {
    "connections": {"default": Settings.DATABASE_URL},
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
