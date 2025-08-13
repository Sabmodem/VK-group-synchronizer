"""
Доменные исключения для бизнес-логики синхронизации групп
"""


class DomainException(Exception):
    """Базовое исключение домена"""
    pass


class ValidationException(DomainException):
    """Ошибка валидации доменных данных"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field


class GroupNotFoundException(DomainException):
    """Группа не найдена"""
    
    def __init__(self, group_id: str):
        super().__init__(f"Группа с ID {group_id} не найдена")
        self.group_id = group_id


class InvalidGroupDataException(ValidationException):
    """Некорректные данные группы"""
    pass


class SyncException(DomainException):
    """Ошибка синхронизации"""
    pass


class ExternalServiceException(DomainException):
    """Ошибка внешнего сервиса (VK API, Google Sheets)"""
    
    def __init__(self, message: str, service: str, retry_after: int = None):
        super().__init__(message)
        self.service = service
        self.retry_after = retry_after  # Секунд до повторной попытки


class RateLimitException(ExternalServiceException):
    """Превышен лимит запросов"""
    
    def __init__(self, service: str, retry_after: int):
        super().__init__(f"Превышен лимит запросов для {service}", service, retry_after)


class CaptchaRequiredException(ExternalServiceException):
    """Требуется решение капчи"""
    
    def __init__(self, captcha_sid: str, captcha_img: str):
        super().__init__("Требуется решение капчи", "VK API")
        self.captcha_sid = captcha_sid
        self.captcha_img = captcha_img

class ValidationRequiredException(ExternalServiceException):
    """Требуется валидация"""
    
    def __init__(self, redirect_uri: str):
        super().__init__("Требуется валидация", "VK API")
        self.redirect_uri = redirect_uri
