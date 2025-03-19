from app.GSSDK import GSRequest

API_KEY = "4_kQKX1P9doAvP4x3kfd9N6g"
SECRET_KEY = "AQQCnE0YaT4aqFser4a+KXqLu4X14JyWbGZHEegujWA="


def send_notify_login_request(site_uid: str):
    method = "accounts.notifyLogin"
    params = {"siteUID": site_uid, "format": "json"}

    request = GSRequest(API_KEY, SECRET_KEY, method, params, useHTTPS=True)
    response = request.send()

    if response.getErrorCode() != 206001:
        raise Exception(
            f"Error in accounts.notifyLogin (Error Code {response.getErrorCode()}): {response.getErrorMessage()}"
        )

    return response.getData().get("regToken")


def send_set_account_info_request(
    reg_token: str,
    first_name: str,
    last_name: str,
    email: str,
    terms: dict,
):
    method = "accounts.setAccountInfo"
    params = {
        "regToken": reg_token,
        "profile": {"firstName": first_name, "lastName": last_name, "email": email},
        "preferences": {
            "terms": terms,
        },
        "format": "json",
    }

    request = GSRequest(API_KEY, SECRET_KEY, method, params, useHTTPS=True)
    response = request.send()

    if response.getErrorCode() != 0:
        raise Exception(
            f"Error in accounts.setAccountInfo (Error Code {response.getErrorCode()}): {response.getErrorMessage()}"
        )


def send_finalize_registration_request(reg_token: str):
    method = "accounts.finalizeRegistration"
    params = {
        "regToken": reg_token,
        "format": "json",
    }

    request = GSRequest(API_KEY, SECRET_KEY, method, params, useHTTPS=True)
    response = request.send()

    if response.getErrorCode() != 0:
        raise Exception(
            f"Error in accounts.finalizeRegistration (Error Code {response.getErrorCode()}): {response.getErrorMessage()}"
        )
