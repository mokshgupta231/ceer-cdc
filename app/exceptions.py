class LoginNotificationException(Exception):
    def __init__(self, message: str, reg_token: str):
        super().__init__(message)
        self.reg_token = reg_token
