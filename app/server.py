from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from starlette.authentication import AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware

from .authentication.middleware import JWTAuthentication
from .authentication.routes import router
from .base.middlewares import dbsession_middleware
from .decode_task.decode_task import router as decode_router
from .posts.routes import router as post_router


def get_application() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.include_router(post_router)
    app.include_router(decode_router)

    app.middleware("http")(dbsession_middleware)

    @app.get("/")
    async def starter(request: Request):
        return {"msg": "ok"}

    return app


app = get_application()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthentication())
add_pagination(app)


@app.exception_handler(AuthenticationError)
async def authentication_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        content={"message": str(exc)}, status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.exception_handler(Exception)
async def handle(request: Request, exc: Exception):
    return JSONResponse(content=1, status_code=status.HTTP_418_IM_A_TEAPOT)
