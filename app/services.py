from app.utils import (
    send_register_request,
)


def register_service(request):
    return send_register_request(site_uid=request.site_uid)
