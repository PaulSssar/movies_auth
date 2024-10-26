from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.postgres import get_session
from src.models.user import User
from services.ya_oauth import get_yandex_oauth_url, get_yandex_token, \
    get_yandex_user_info

router = APIRouter()


@router.get("/login/yandex")
async def yandex_login():
    oauth_url = get_yandex_oauth_url()
    return RedirectResponse(url=oauth_url)


@router.get("/callback/yandex")
async def yandex_callback(request: Request,
                          db: AsyncSession = Depends(get_session)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400,
                            detail="Code not provided by Yandex")

    token = await get_yandex_token(code)
    if not token:
        raise HTTPException(status_code=400,
                            detail="Failed to obtain token from Yandex")

    user_info = await get_yandex_user_info(token)
    if not user_info:
        raise HTTPException(status_code=400,
                            detail="Failed to obtain user info from Yandex")

    yandex_id = user_info.get('id')
    yandex_email = user_info.get('default_email')

    user_query = select(User).filter(User.yandex_id == yandex_id)
    user = (await db.execute(user_query)).scalars().first()

    if not user:
        user = User(
            login=user_info.get('login') or user_info.get('display_name'),
            password='placeholder_password',
            first_name=user_info.get('first_name', ''),
            last_name=user_info.get('last_name', ''),
            yandex_id=yandex_id,
            yandex_email=yandex_email
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        user.yandex_email = yandex_email
        await db.commit()

    return {"message": "Yandex login successful",
            "user": {"id": user.id, "yandex_email": user.yandex_email}}
