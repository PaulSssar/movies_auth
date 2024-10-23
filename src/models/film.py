from datetime import datetime

from pydantic import BaseModel


class Film(BaseModel):
    id: str
    title: str
    description: str | None
    created: datetime | None = None
    imdb_rating: float
    genres: list | None
    directors: list | None
    actors: list
    writers: list


class Films(BaseModel):
    items: list[Film]

