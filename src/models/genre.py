from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    title: str
    rating: float = 0.0


class Genres(BaseModel):
    items: list[Genre]

