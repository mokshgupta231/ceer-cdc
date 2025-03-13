from app.utils import send_lite_register_request, send_set_account_info_request


def lite_register_service(request):
    return send_lite_register_request(site_uid=request.site_uid)


def set_account_info_service(request):
    send_set_account_info_request(
        reg_token=request.reg_token,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
    )
