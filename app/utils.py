from app.GSSDK import GSRequest

API_KEY = "4_kQKX1P9doAvP4x3kfd9N6g"
SECRET_KEY = "AQQCnE0YaT4aqFser4a+KXqLu4X14JyWbGZHEegujWA="


def send_register_request(email: str, password: str, first_name: str, last_name: str):
    method = "accounts.register"
    params = {
        "email": email,
        "password": password,
        "profile": {"firstName": first_name, "lastName": last_name},
        "finalizeRegistration": True,
    }

    request = GSRequest(API_KEY, SECRET_KEY, method, params)
    response = request.send()

    if response.getErrorCode() not in (0, 206002):
        raise Exception(f"Error in accounts.register: {response.getErrorMessage()}")


def send_login_request(email: str, password: str):
    method = "accounts.login"
    params = {"loginID": email, "password": password}

    request = GSRequest(API_KEY, SECRET_KEY, method, params)
    response = request.send()

    if response.getErrorCode() != 0:
        raise Exception(f"Error in accounts.login: {response.getErrorMessage()}")

    return response.getData()


def send_reset_password_request(email: str):
    method = "accounts.resetPassword"
    params = {"loginID": email}

    request = GSRequest(API_KEY, SECRET_KEY, method, params)
    response = request.send()

    if response.getErrorCode() != 0:
        raise Exception(
            f"Error in accounts.resetPassword: {response.getErrorMessage()}"
        )
