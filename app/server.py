from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.authentication import AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware

from .authentication.middleware import JWTAuthentication
from .authentication.routes import router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthentication())
app.include_router(router)


@app.get("/")
async def starter(request: Request):
    return {"msg": "ok"}


@app.exception_handler(AuthenticationError)
async def authentication_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        content={"message": str(exc)}, status_code=status.HTTP_401_UNAUTHORIZED
    )
