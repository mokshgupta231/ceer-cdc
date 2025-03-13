from fastapi import APIRouter, HTTPException
from app.models import RegisterRequest, SetAccountInfoRequest
from app.services import register_service, set_account_info_service

router = APIRouter()


@router.post("/register/")
def register(request: RegisterRequest):
    try:
        reg_token = register_service(request)
        return {"msg": "Lite registration successful", "reg_token": reg_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-account-info/")
def register(request: SetAccountInfoRequest):
    try:
        user_data = set_account_info_service(request)
        return {"msg": "Account information updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
