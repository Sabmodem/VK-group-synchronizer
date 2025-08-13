import asyncio
from typing import Optional
from infrastructure.interfaces.captcha_solver import CaptchaSolver


class DummyCaptchaSolver(CaptchaSolver):
    """
    Заглушка для решения капчи (для тестирования)
    
    Всегда возвращает заданный текст или None
    """
    
    def __init__(self, dummy_response: Optional[str] = None):
        """
        Инициализация заглушки
        
        Args:
            dummy_response: Текст который будет возвращен как решение капчи
        """
        self.dummy_response = dummy_response
    
    async def solve_captcha(self, captcha_sid: str, captcha_img: str) -> Optional[str]:
        """Возвращает заранее заданный ответ"""
        print(f"🧪 ТЕСТОВЫЙ РЕЖИМ: Капча SID={captcha_sid}")
        print(f"🧪 Изображение: {captcha_img}")
        print(f"🧪 Возвращаем: {self.dummy_response}")
        return self.dummy_response
    
    def get_solver_name(self) -> str:
        """Возвращает название решателя"""
        return "Тестовая заглушка для капчи"
