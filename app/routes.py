from fastapi import APIRouter, HTTPException
from app.models import RegisterRequest, SetAccountInfoRequest
from app.services import lite_register_service, set_account_info_service

router = APIRouter()


@router.post("/lite-register/")
def lite_register(request: RegisterRequest):
    try:
        reg_token = lite_register_service(request)
        return {"msg": "Lite registration successful", "reg_token": reg_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-account-info/")
def register(request: SetAccountInfoRequest):
    try:
        set_account_info_service(request)
        return {"msg": "Account information updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
