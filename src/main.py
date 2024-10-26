import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from api import users, roles
from api.v1 import films, persons, genres, oauth
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


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)
FastAPIInstrumentor.instrument_app(app)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return response


app.include_router(users.router, prefix='/api/users', tags=['users'])
app.include_router(roles.router, prefix='/api/roles', tags=['roles'])

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])

app.include_router(oauth.router, prefix='/api/v1/oauth', tags=['oauth'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
