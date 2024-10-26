from http import HTTPStatus
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from models import User
from services.decorators import authentication_required
from services.film import FilmService, get_film_service
from services.users import get_current_user

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    description: Optional[str]


class FilmItem(BaseModel):
    id: str
    title: str


class Films(BaseModel):
    result: list[FilmItem]


@router.get('/', response_model=Films)
@authentication_required
async def films_list(
        page_number: Annotated[int, Query(title="Page number", ge=0)] = 1,
        page_size: Annotated[int, Query(title="Page size", ge=2, le=50)] = 50,
        sort: str = Query(''),
        order: str = Query(''),
        film_service: FilmService = Depends(get_film_service),
        current_user: User =Depends(get_current_user)
) -> Films:
    films = await film_service.get_items(
        page_size=page_size,
        page_number=page_number,
        sort=sort,
        order=order
    )
    return Films(
        result=[FilmItem(id=film.id, title=film.title) for film in films]
    )


@router.get('/search', response_model=Films)
@authentication_required
async def film_search(
        page_number: Annotated[int, Query(title="Page number", ge=0)] = 1,
        page_size: Annotated[int, Query(title="Page size", ge=2, le=50)] = 50,
        sort: str = Query(''),
        query: str = Query(None),
        film_service: FilmService = Depends(get_film_service),
        order: str = Query(''),
        current_user: User =Depends(get_current_user)
) -> Films:
    films = await film_service.get_items(
        query=query,
        page_size=page_size,
        page_number=page_number,
        sort=sort,
        order=order
    )
    return Films(
        result=[FilmItem(id=film.id, title=film.title) for film in films]
    )


@router.get('/{film_id}', response_model=Film)
@authentication_required
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service),
        current_user: User =Depends(get_current_user)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )
    return Film(id=film_id, title=film.title, description=film.description)
