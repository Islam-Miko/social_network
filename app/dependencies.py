from fastapi import HTTPException, Request, status

from app.messages import NOT_AUTHENTICATED


async def check_authenticated(request: Request):
    if request.user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=NOT_AUTHENTICATED
        )
