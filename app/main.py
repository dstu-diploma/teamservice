from app.dependencies import get_event_consumer, get_event_publisher
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.events import register_events
from app.routers import main_router
from app.config import Settings
from fastapi import FastAPI
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = get_event_consumer()
    publisher = get_event_publisher()

    await publisher.connect()
    await consumer.connect()

    task = await register_events(consumer)

    yield

    task.cancel()
    await task


app = FastAPI(
    title="DSTU Diploma | TeamService",
    docs_url="/swagger",
    root_path=Settings.ROOT_PATH,
    lifespan=lifespan,
)

init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
