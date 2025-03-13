from fastapi import APIRouter, HTTPException
from app.models import LoginRequest, RegisterRequest, ResetPasswordRequest
from app.services import login_service, register_service, reset_password_service

router = APIRouter()


@router.post("/register/")
def register(request: RegisterRequest):
    try:
        register_service(request)
        return {"msg": "Registration successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/")
def login(request: LoginRequest):
    try:
        user_data = login_service(request)
        return {"msg": "Login successful", "user": user_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-password/")
def reset_password(request: ResetPasswordRequest):
    try:
        result = reset_password_service(request)
        return {"msg": "Reset password mail sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
