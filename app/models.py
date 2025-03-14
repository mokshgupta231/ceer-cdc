from pydantic import BaseModel


class NotifyLoginRequest(BaseModel):
    site_uid: str


class SetAccountInfoRequest(BaseModel):
    reg_token: str
    first_name: str
    last_name: str
    email: str


class FinalizeRegistrationRequest(BaseModel):
    reg_token: str
