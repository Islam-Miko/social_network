from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette.authentication import AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware

from app.middlewares.authentication import JWTAuthentication
from app.routes.v2.authentication import router
from app.routes.v2.post_routes import router as post_router

reuseable_oauth = HTTPBearer(bearerFormat="JWT")


def get_application() -> FastAPI:

    app = FastAPI()
    app.include_router(post_router, dependencies=[Depends(reuseable_oauth)])
    app.include_router(router, prefix="/api/v2")

    @app.get("/", dependencies=[Depends(reuseable_oauth)])
    async def starter(request: Request):
        return {"msg": request.user}

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


@app.exception_handler(AuthenticationError)
async def authentication_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        content={"message": str(exc)}, status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.exception_handler(Exception)
async def handle(request: Request, exc: Exception):
    return JSONResponse(content=1, status_code=status.HTTP_418_IM_A_TEAPOT)
