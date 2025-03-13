from fastapi import APIRouter, HTTPException
from app.models import RegisterRequest
from app.services import register_service

router = APIRouter()


@router.post("/register/")
def register(request: RegisterRequest):
    try:
        user_data = register_service(request)
        return {"msg": "Registration successful", "user": user_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
