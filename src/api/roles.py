from http import HTTPStatus
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel

from models import User
from services.roles import RoleService, get_role_service
from services.decorators import superuser_required
from services.users import get_current_user

router = APIRouter()


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleInDB(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/roles/", response_model=RoleInDB, status_code=HTTPStatus.CREATED,
             dependencies=[Depends(RateLimiter(times=5, seconds=60))])
@superuser_required
async def create_role(
    role: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user)
):
    new_role = await role_service.create_role(name=role.name, description=role.description)
    return new_role


@router.get("/roles/", response_model=List[RoleInDB],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_roles(
    role_service: RoleService = Depends(get_role_service),
):
    roles = await role_service.get_roles()
    return roles


@router.get("/roles/{role_id}", response_model=RoleInDB,
            dependencies=[Depends(RateLimiter(times=15, seconds=60))])
async def get_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
):
    role = await role_service.get_role(role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Role not found."
        )
    return role


@router.put("/roles/{role_id}", response_model=RoleInDB,
            dependencies=[Depends(RateLimiter(times=5, seconds=60))])
@superuser_required
async def update_role(
    role_id: UUID,
    role: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user)
):
    updated_role = await role_service.update_role(role_id=role_id, name=role.name, description=role.description)
    return updated_role


@router.delete("/roles/{role_id}", status_code=HTTPStatus.NO_CONTENT,
               dependencies=[Depends(RateLimiter(times=3, seconds=60))])
@superuser_required
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user)
):
    await role_service.delete_role(role_id=role_id)
