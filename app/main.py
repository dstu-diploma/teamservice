from fastapi.middleware.cors import CORSMiddleware
from app.views import main_router
from fastapi import FastAPI
from app.db import init_db
from os import environ


ROOT_PATH = environ.get("ROOT_PATH", "")

app = FastAPI(
    title="DSTU Diploma | TeamService", docs_url="/swagger", root_path=ROOT_PATH
)
init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
