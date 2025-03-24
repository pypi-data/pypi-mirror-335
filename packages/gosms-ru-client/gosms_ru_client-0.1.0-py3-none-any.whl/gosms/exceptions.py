from typing import Optional

class GoSMSError(Exception):
    """Базовый класс для ошибок GoSMS API"""
    def __init__(self, code: int, message: str, hash: Optional[str] = None):
        self.code = code
        self.message = message
        self.hash = hash
        super().__init__(f"[{code}] {message}")

class AuthenticationError(GoSMSError):
    """Ошибка аутентификации"""
    pass

class RateLimitError(GoSMSError):
    """Ошибка превышения лимита запросов"""
    pass

class ValidationError(GoSMSError):
    """Ошибка валидации данных"""
    pass

class ResourceNotFoundError(GoSMSError):
    """Ошибка отсутствия ресурса"""
    pass 