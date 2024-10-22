import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import users, roles
from api.v1 import films, persons, genres
from core.config import settings
from core.logger import LOGGING
from db import db_cache, db_storage
from db.elastic.EsStorage import EsStorage
from db.redis.redis_cache import RedisCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_cache.cache = RedisCache()
    db_storage.storage = EsStorage()
    await db_storage.storage.open()

    yield

    await db_cache.cache.close()
    if db_storage.storage:
        await db_storage.storage.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(users.router, prefix='/api/users', tags=['users'])
app.include_router(roles.router, prefix='/api/roles', tags=['roles'])

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
