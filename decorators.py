from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException


def validate_auth(func):
    def wrapper(Authorize:AuthJWT=Depends(), *args, **kwargs):
        try:
            Authorize.jwt_required()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
        return func(*args, **kwargs)
    return wrapper