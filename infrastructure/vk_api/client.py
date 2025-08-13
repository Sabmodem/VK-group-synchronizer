from typing import Optional, Dict, Any
import aiohttp
import json

from domain.exceptions import ExternalServiceException, RateLimitException, CaptchaRequiredException, ValidationRequiredException
from infrastructure.interfaces.captcha_solver import CaptchaSolver

import asyncio

class VKAPIClient:
    """
    Клиент для работы с VK API
    
    Обеспечивает базовые HTTP запросы к VK API с обработкой ошибок и решением капчи
    """

    def __init__(
        self, 
        access_token: str, 
        api_version: str = "5.131",
        captcha_solver: Optional[CaptchaSolver] = None
    ):
        """
        Инициализация клиента
        
        Args:
            access_token: Токен доступа VK API
            api_version: Версия VK API
            captcha_solver: Решатель капчи (если None, капча не решается автоматически)
        """
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = "https://api.vk.com/method"
        self.captcha_solver = captcha_solver
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получает HTTP сессию с ленивой инициализацией"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'VK-Groups-Sync/1.0'
                }
            )
        return self._session

    async def call_method(
        self,
        method: str,
        params: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Выполняет вызов метода VK API с обработкой капчи
        
        Args:
            method: Название метода VK API (например, "groups.create")
            params: Параметры запроса
            **kwargs: Дополнительные параметры
            
        Returns:
            Dict: Ответ VK API
            
        Raises:
            ExternalServiceException: При ошибке API
            RateLimitException: При превышении лимитов
            CaptchaRequiredException: При необходимости ввода капчи (если нет решателя)
        """
        if params is None:
            params = {}

        # Добавляем обязательные параметры
        request_params = {
            'access_token': self.access_token,
            'v': self.api_version,
            **params,
            **kwargs
        }

        # Пробуем выполнить запрос с автоматической обработкой капчи
        max_captcha_attempts = 3
        max_rate_limit_attempts = 3
        captcha_attempt = 0
        rate_limit_attempt = 0
        
        while captcha_attempt <= max_captcha_attempts and rate_limit_attempt <= max_rate_limit_attempts:
            try:
                return await self._execute_request(method, request_params)
                
            except CaptchaRequiredException as e:
                captcha_attempt += 1
                
                # Если нет решателя капчи, пробрасываем исключение
                if self.captcha_solver is None:
                    print(f"⚠️  Требуется решение капчи, но решатель не настроен")
                    print(f"Откройте ссылку: {e.captcha_img}")
                    raise e
                
                # Если превышено количество попыток
                if captcha_attempt > max_captcha_attempts:
                    print(f"❌ Превышено максимальное количество попыток решения капчи ({max_captcha_attempts})")
                    raise ExternalServiceException(
                        f"Не удалось решить капчу за {max_captcha_attempts} попыток",
                        "VK API"
                    )
                
                print(f"🛡️  Обнаружена капча (попытка {captcha_attempt}/{max_captcha_attempts})")
                print(f"Решатель: {self.captcha_solver.get_solver_name()}")
                
                # Решаем капчу
                captcha_key = await self.captcha_solver.solve_captcha(e.captcha_sid, e.captcha_img)
                
                if captcha_key is None:
                    print("❌ Капча не была решена")
                    raise ExternalServiceException(
                        "Пользователь отменил решение капчи",
                        "VK API"
                    )
                
                # Добавляем параметры капчи к запросу
                request_params['captcha_sid'] = e.captcha_sid
                request_params['captcha_key'] = captcha_key
                
                print(f"🔑 Капча решена, повторяем запрос...")
                continue
            except ValidationRequiredException as e:
                captcha_attempt += 1
                print(f"⚠️  Требуется валидация, но обработчик валидации не настроен")
                print(f"Откройте ссылку: {e.redirect_uri}")
                raise e
            except RateLimitException as e:
                rate_limit_attempt += 1
                print(f"⚠️  Превышен лимит запросов")
                print(f"Ожидание: {e.retry_after} секунд")
                await asyncio.sleep(e.retry_after)
                continue

    
    async def _execute_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет HTTP запрос к VK API
        
        Args:
            method: Название метода VK API
            params: Параметры запроса
            
        Returns:
            Dict: Ответ VK API
            
        Raises:
            ExternalServiceException: При HTTP ошибках
            CaptchaRequiredException: При необходимости решения капчи
            RateLimitException: При превышении лимитов
        """
        url = f"{self.base_url}/{method}"
        
        try:
            session = await self._get_session()
            
            async with session.post(url, data=params) as response:
                if response.status != 200:
                    raise ExternalServiceException(
                        f"HTTP ошибка {response.status}: {response.reason}",
                        "VK API"
                    )
                
                response_data = await response.json()
                
                # Проверяем на ошибки VK API
                if 'error' in response_data:
                    await self._handle_vk_error(response_data['error'])
                
                return response_data.get('response', {})
                
        except aiohttp.ClientError as e:
            raise ExternalServiceException(
                f"Ошибка HTTP клиента: {e}",
                "VK API"
            )
        except json.JSONDecodeError as e:
            raise ExternalServiceException(
                f"Некорректный JSON ответ от VK API: {e}",
                "VK API"
            )
    
    async def _handle_vk_error(self, error: Dict[str, Any]) -> None:
        """
        Обрабатывает ошибки VK API
        
        Args:
            error: Словарь с информацией об ошибке
            
        Raises:
            Соответствующее исключение в зависимости от типа ошибки
        """
        error_code = error.get('error_code', 0)
        error_msg = error.get('error_msg', 'Unknown error')
        
        # Обработка капчи
        if error_code == 14:  # Captcha needed
            captcha_sid = error.get('captcha_sid', '')
            captcha_img = error.get('captcha_img', '')
            raise CaptchaRequiredException(captcha_sid, captcha_img)
        
        # Обработка лимитов запросов
        elif error_code == 6:  # Too many requests per second
            raise RateLimitException("VK API", 5)  # Подождать 5 секунд
        
        # Обработка лимитов в сутки
        elif error_code == 9:  # Flood control
            raise RateLimitException("VK API", 60)  # Подождать минуту
        
        # Обработка других ошибок
        elif error_code == 5:  # User authorization failed
            raise ExternalServiceException(
                "Ошибка авторизации: проверьте токен доступа",
                "VK API"
            )
        
        elif error_code == 15:  # Access denied
            raise ExternalServiceException(
                f"Доступ запрещен: {error_msg}",
                "VK API"
            )
        
        elif error_code == 100:  # One of the parameters specified was missing or invalid
            raise ExternalServiceException(
                f"Некорректные параметры запроса: {error_msg}",
                "VK API"
            )
        
        elif error_code == 17:
            redirect_uri = error.get('redirect_uri', '')
            raise ValidationRequiredException(redirect_uri)
 
        else:
            # Общая ошибка API
            raise ExternalServiceException(
                f"Ошибка VK API [{error_code}]: {error_msg}",
                "VK API"
            )
    
    async def upload_photo(self, upload_url: str, photo_data: bytes) -> Dict[str, Any]:
        """
        Загружает фото по URL загрузки
        
        Args:
            upload_url: URL для загрузки фото
            photo_data: Данные фото в виде bytes
            
        Returns:
            Dict: Ответ сервера загрузки
        """
        try:
            session = await self._get_session()
            
            # Создаем multipart form data
            data = aiohttp.FormData()
            data.add_field('photo', photo_data, filename='avatar.jpg', content_type='image/jpeg')
            
            async with session.post(upload_url, data=data) as response:
                if response.status != 200:
                    raise ExternalServiceException(
                        f"Ошибка загрузки фото: HTTP {response.status}",
                        "VK API"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise ExternalServiceException(
                f"Ошибка загрузки фото: {e}",
                "VK API"
            )
    
    def set_captcha_solver(self, captcha_solver: Optional[CaptchaSolver]) -> None:
        """
        Устанавливает решатель капчи
        
        Args:
            captcha_solver: Новый решатель капчи или None для отключения
        """
        self.captcha_solver = captcha_solver
        if captcha_solver:
            print(f"🛡️  Установлен решатель капчи: {captcha_solver.get_solver_name()}")
        else:
            print("🛡️  Решатель капчи отключен")
    
    async def close(self):
        """Закрывает HTTP сессию"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Контекстный менеджер для автоматического закрытия сессии"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Автоматически закрывает сессию при выходе из контекста"""
        await self.close()
