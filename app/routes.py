from fastapi import APIRouter, HTTPException
from app.models import (
    FinalizeRegistrationRequest,
    NotifyLoginRequest,
    SetAccountInfoRequest,
)
from app.services import (
    finalize_registration_service,
    notify_login_service,
    set_account_info_service,
)

router = APIRouter()


@router.post("/notify-login/")
def notify_login(request: NotifyLoginRequest):
    try:
        reg_token = notify_login_service(request)
        return {"msg": "Login notification successful", "reg_token": reg_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-account-info/")
def register(request: SetAccountInfoRequest):
    try:
        set_account_info_service(request)
        return {"msg": "Account information updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finalize-registration/")
def finalize_registration(request: FinalizeRegistrationRequest):
    try:
        finalize_registration_service(request)
        return {"msg": "Registration finalized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
