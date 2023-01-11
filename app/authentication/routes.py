from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app import messages

from ..base.repositories import SqlAlchemyRepository
from ..db import async_session
from .models import Credential, RefreshToken, User
from .schema import AuthenticationSchema, RegistrationSchema, TokensSchema
from .services import (
    AuthenticationHandler,
    PasswordHandler,
    get_authentication_handler,
)

router = APIRouter(prefix="/auth")


@router.post("/access-token/", response_model=TokensSchema)
async def generate_access_token(
    data: AuthenticationSchema,
    auth: AuthenticationHandler = Depends(get_authentication_handler),
):
    user_credential = await auth.authorize(**data.dict())
    access_token, _ = await auth.generate_token(
        data={"user": user_credential.login}
    )
    refresh_token, exp_at = await auth.generate_token(
        token_type="refresh", data={"user": user_credential.id}
    )
    _, key, _ = refresh_token.split(".")
    session = async_session()
    repo = SqlAlchemyRepository(session, RefreshToken)

    refresh = await repo.get_or_none(  # type: ignore
        RefreshToken.owner == user_credential.id
    )
    if refresh is not None:
        await repo.force_delete(refresh.id)  # type: ignore
    await repo.create(key=key, owner=user_credential.id, valid_until=exp_at)  # type: ignore
    await session.commit()
    return TokensSchema(access_token=access_token, refresh_token=refresh_token)


@router.post("/register/")
async def register_user(data: RegistrationSchema):
    session = async_session()
    repo = SqlAlchemyRepository(session, Credential)
    user_repo = SqlAlchemyRepository(session, User)
    user_credentials = await repo.get_or_none(Credential.login == data.login)  # type: ignore

    if user_credentials is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": messages.ALREADY_REGISTERED},
        )

    password_hash = PasswordHandler.get_hash(data.password)
    user = await user_repo.create(**data.dict(exclude={"login", "password"}))
    await repo.create(login=data.login, password=password_hash, id=user.id)
    await session.commit()
    return JSONResponse(
        status_code=200, content={"message": messages.SUCCESSFULLY_REGISTERED}
    )


@router.post(
    "/refresh-token/",
    response_model=TokensSchema,
    response_model_include={"access_token"},
)
async def refresh_token(
    data: TokensSchema,
    auth: AuthenticationHandler = Depends(get_authentication_handler),
):
    access_token, _ = await auth.refresh_token(**data.dict())
    return TokensSchema(access_token=access_token, refresh_token="")
