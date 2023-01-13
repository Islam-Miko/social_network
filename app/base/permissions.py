import abc
from functools import wraps
from typing import Iterable, Type

from fastapi import HTTPException, Request, status

from ..messages import NO_PERMISSION


class BasePermission(abc.ABC):
    @abc.abstractclassmethod
    async def has_permission(cls, request: Request) -> bool:
        raise NotImplementedError()


class PermissionsHandler:
    """
    Class for checking permissions
    """

    def __init__(
        self,
        permission_classes: Iterable[Type[BasePermission]],
    ):
        self.permission_classes = permission_classes

    async def check_permissions(self, request: Request):
        has_permission = await self.__check_permissions(request)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=NO_PERMISSION
            )

    async def __check_permissions(self, request: Request) -> bool:
        for perm in self.permission_classes:
            result = await perm.has_permission(request)
            if result is False:
                return False
        return True


class IsAuthenticated(BasePermission):
    @classmethod
    async def has_permission(cls, request: Request) -> bool:  # type: ignore
        return request.user is not None


class AllowAny(BasePermission):
    @classmethod
    async def has_permission(cls, request: Request) -> bool:  # type: ignore
        return True


def permission_classes(permissions: Iterable[Type[BasePermission]]):
    """
    Register Permissions on endpoint.
    Permission.has_permission will be called, before endpoint function call
    """

    def decorator_permission(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            permission_handler = PermissionsHandler(permissions)
            await permission_handler.check_permissions(request)
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator_permission
