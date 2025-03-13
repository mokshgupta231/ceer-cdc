from pydantic import BaseModel


class RegisterRequest(BaseModel):
    site_uid: str
