import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import users
from core.config import settings
from core.logger import LOGGING
from db import db_cache
from db.postgres import create_database, purge_database
from db.redis.RedisCache import RedisCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_cache.cache = RedisCache(settings.redis_host, settings.redis_port)
    import models
    await create_database()

    yield

    await db_cache.cache.close()
    await purge_database()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(users.router, prefix='/api/users', tags=['users'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
