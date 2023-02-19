from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app import messages
from app.schemas.auth_schema import (
    AuthenticationSchema,
    RegistrationSchema,
    TokensSchema,
)
from app.services.auth_services import AuthService
from app.services.user_service import (
    CredentialService,
    RefreshTokenService,
    UserService,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokensSchema)
async def create_tokens(
    data: AuthenticationSchema,
    service: AuthService = Depends(),
    credential_service: CredentialService = Depends(),
    refresh_service: RefreshTokenService = Depends(),
):
    return await service.access_token(
        data, credential_service, refresh_service
    )


@router.post("/register/")
async def register_user(
    data: RegistrationSchema,
    service: AuthService = Depends(),
    credential_service: CredentialService = Depends(),
    user_service: UserService = Depends(),
):
    await service.register(data, user_service, credential_service)
    return JSONResponse(
        status_code=201, content={"message": messages.SUCCESSFULLY_REGISTERED}
    )


@router.post(
    "/refresh-token/",
    response_model=TokensSchema,
    response_model_include={"access_token"},
)
async def refresh_token(
    data: TokensSchema,
    service: AuthService = Depends(),
    refresh_service: RefreshTokenService = Depends(),
):
    return await service.generate_new(data, service=refresh_service)
