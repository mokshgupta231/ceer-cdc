from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ResetPasswordRequest(BaseModel):
    email: str
