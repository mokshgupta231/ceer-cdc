from app.utils import (
    send_register_request,
    send_login_request,
    send_reset_password_request,
)


def register_service(request):
    send_register_request(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
    )


def login_service(request):
    return send_login_request(email=request.email, password=request.password)


def reset_password_service(request):
    send_reset_password_request(email=request.email)
