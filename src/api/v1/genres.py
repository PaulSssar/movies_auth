from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Annotated

from models import User
from services.decorators import authentication_required
from services.genre import GenreService, get_genre_service
from services.users import get_current_user

router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str]


class Genres(BaseModel):
    result: List[Genre]


@router.get('/', response_model=Genres)
@authentication_required
async def genres_list(
        page_number: Annotated[int, Query(title="Page number", ge=1)],
        page_size: Annotated[int, Query(title="Page size", ge=2, le=50)],
        sort: str = Query(''),
        query: Optional[str] = Query(None),
        genre_service: GenreService = Depends(get_genre_service),
        current_user: User =Depends(get_current_user)
) -> Genres:
    genres = await genre_service.get_items(
        query=query,
        page_size=page_size,
        page_number=page_number,
        sort=sort
    )
    return Genres(result=genres)


@router.get('/{genre_id}', response_model=Genre)
@authentication_required
async def genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service),
        current_user: User =Depends(get_current_user)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Genre not found")
    return Genre(id=genre_id, name=genre['name'],
                 description=genre.get('description'))
