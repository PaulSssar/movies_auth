from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.config import settings
from src.db.postgres import get_session
from src.models.user import User
from src.services.oauth.oauth_utils import get_oauth_url, get_token
from src.services.oauth.oauth_service import  OAuthService

router = APIRouter()


@router.get("/login")
async def login():
    provider_name = settings.authorize_provider
    try:
        oauth_url = get_oauth_url(provider_name=provider_name)
        return RedirectResponse(url=oauth_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback")
async def callback(request: Request,
                          db: AsyncSession = Depends(get_session)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400,
                            detail=f"Code not provided by OAuth provider")

    provider_name = settings.authorize_provider
    token = await get_token(provider_name=provider_name, code=code)
    if not token:
        raise HTTPException(status_code=400,
                            detail=f"Failed to obtain token "
                                   f"from {provider_name}")

    oauth_service = OAuthService(provider_name=provider_name)
    user_info = await oauth_service.get_user_info(token)

    if not user_info:
        raise HTTPException(status_code=400,
                            detail=f"Failed to obtain user info "
                                   f"from {provider_name}")

    user_id = user_info.get('id')
    user_email = user_info.get('default_email')

    user_query = select(User).filter(User.user_id == user_id)
    user = (await db.execute(user_query)).scalars().first()

    if not user:
        user = User(
            login=user_info.get('login') or user_info.get('display_name'),
            password='placeholder_password',
            first_name=user_info.get('first_name', ''),
            last_name=user_info.get('last_name', ''),
            user_id=user_id,
            user_email=user_email
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return {"message": f"{provider_name} login successful",
            "user": {"id": user.id, "user_email": user.user_email}}
