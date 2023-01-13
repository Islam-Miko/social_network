from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app import messages

from ..base.repositories import SqlAlchemyRepository
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
    request: Request,
    data: AuthenticationSchema,
    auth: AuthenticationHandler = Depends(get_authentication_handler),
):
    session = request.state.dbsession()
    user_credential = await auth.authorize(**data.dict(), session=session)
    access_token, _ = await auth.generate_token(
        data={"user": user_credential.login}
    )
    refresh_token, exp_at = await auth.generate_token(
        token_type="refresh", data={"user": user_credential.id}
    )
    _, key, _ = refresh_token.split(".")
    repo = SqlAlchemyRepository(session, RefreshToken)

    refresh = await repo.get_or_none(  # type: ignore
        RefreshToken.owner == user_credential.id
    )
    if refresh is not None:
        await repo.force_delete(RefreshToken.id == refresh.id)  # type: ignore
    await repo.create(key=key, owner=user_credential.id, valid_until=exp_at)  # type: ignore
    await session.commit()
    await session.close()
    return TokensSchema(access_token=access_token, refresh_token=refresh_token)


@router.post("/register/")
async def register_user(request: Request, data: RegistrationSchema):
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Credential)
    user_repo = SqlAlchemyRepository(session, User)
    user_credentials = await repo.get_or_none(Credential.login == data.login)  # type: ignore

    if user_credentials is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.ALREADY_REGISTERED,
        )

    password_hash = PasswordHandler.get_hash(data.password)
    user = await user_repo.create(**data.dict(exclude={"login", "password"}))
    await repo.create(**dict(login=data.login, password=password_hash, id=user.id))  # type: ignore
    await session.commit()
    await session.close()
    return JSONResponse(
        status_code=201, content={"message": messages.SUCCESSFULLY_REGISTERED}
    )


@router.post(
    "/refresh-token/",
    response_model=TokensSchema,
    response_model_include={"access_token"},
)
async def refresh_token(
    request: Request,
    data: TokensSchema,
    auth: AuthenticationHandler = Depends(get_authentication_handler),
):
    session = request.state.dbsession()
    access_token, _ = await auth.refresh_token(**data.dict(), session=session)
    await session.close()
    return TokensSchema(access_token=access_token, refresh_token="")
