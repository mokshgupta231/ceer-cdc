from app.GSSDK import GSRequest

API_KEY = "4_kQKX1P9doAvP4x3kfd9N6g"
SECRET_KEY = "AQQCnE0YaT4aqFser4a+KXqLu4X14JyWbGZHEegujWA="


def send_register_request(site_uid: str):
    method = "accounts.notifyLogin"
    params = {"siteUID": site_uid, "skipValidation": True, "format": "json"}

    request = GSRequest(API_KEY, SECRET_KEY, method, params, useHTTPS=True)
    response = request.send()

    if response.getErrorCode() != 0:
        raise Exception(f"Error in accounts.notifyLogin: {response.getErrorMessage()}")

    return response.getData()
