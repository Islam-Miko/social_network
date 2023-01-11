from datetime import date

from pydantic import BaseModel


class AuthenticationSchema(BaseModel):
    login: str
    password: str


class RegistrationSchema(AuthenticationSchema):
    first_name: str
    last_name: str
    birth_date: date


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
