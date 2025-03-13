from pydantic import BaseModel


class RegisterRequest(BaseModel):
    site_uid: str


class SetAccountInfoRequest(BaseModel):
    reg_token: str
    first_name: str
    last_name: str
    email: str
