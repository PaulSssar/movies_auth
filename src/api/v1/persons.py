from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Annotated

from models import User
from services.decorators import authentication_required
from services.person import PersonService, get_person_service
from services.users import get_current_user

router = APIRouter()


class Person(BaseModel):
    id: str
    name: str
    description: Optional[str]


class Persons(BaseModel):
    result: List[Person]


@router.get('/', response_model=Persons)
@authentication_required
async def persons_list(
        page_number: Annotated[int, Query(title="Page size", ge=1)],
        page_size: Annotated[int, Query(title="Page size", ge=2, le=50)],
        sort: str = Query(''),
        query: Optional[str] = Query(None),
        person_service: PersonService = Depends(get_person_service),
        current_user: User =Depends(get_current_user)
) -> Persons:
    persons = await person_service.get_items(
        query=query,
        page_size=page_size,
        page_number=page_number,
        sort=sort
    )
    return Persons(result=persons)


@router.get('/{person_id}', response_model=Person)
@authentication_required
async def person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service),
        current_user: User =Depends(get_current_user)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Person not found"
        )
    return Person(
        id=person_id, name=person['name'], description=person.get('description')
    )
