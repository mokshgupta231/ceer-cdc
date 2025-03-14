from app.utils import (
    send_notify_login_request,
    send_set_account_info_request,
    send_finalize_registration_request,
)


def notify_login_service(request):
    return send_notify_login_request(site_uid=request.site_uid)


def set_account_info_service(request):
    send_set_account_info_request(
        reg_token=request.reg_token,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
    )


def finalize_registration_service(request):
    send_finalize_registration_request(reg_token=request.reg_token)
