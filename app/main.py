from fastapi import FastAPI
from app.db import init_db
from app.views import main_router
from os import environ


ROOT_PATH = environ.get('ROOT_PATH', '/')

app = FastAPI(title="DSTU Diploma | TeamService", docs_url="/swagger", root_path=ROOT_PATH)
init_db(app)
app.include_router(main_router)
