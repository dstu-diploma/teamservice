from fastapi import FastAPI
from app.db import init_db
from app.views import main_router

app = FastAPI(title="DSTU Diploma | TeamService", docs_url="/swagger")
init_db(app)
app.include_router(main_router)
