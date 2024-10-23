from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str
    role: str
    film_ids: str


class Persons(BaseModel):
    items: list[Person]

