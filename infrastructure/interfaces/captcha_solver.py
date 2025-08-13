from abc import ABC, abstractmethod
from typing import Optional


class CaptchaSolver(ABC):
    """
    Интерфейс для решения капчи VK API
    
    Позволяет реализовать различные стратегии решения капчи:
    - Интерактивное решение через консоль
    - Автоматическое решение через внешние сервисы
    - И другие варианты
    """
    
    @abstractmethod
    async def solve_captcha(self, captcha_sid: str, captcha_img: str) -> Optional[str]:
        """
        Решает капчу и возвращает текст
        
        Args:
            captcha_sid: ID капчи для повторного запроса
            captcha_img: URL изображения капчи
            
        Returns:
            str: Текст с изображения капчи или None если не удалось решить
        """
        pass
    
    @abstractmethod
    def get_solver_name(self) -> str:
        """
        Возвращает название решателя капчи
        
        Returns:
            str: Человекочитаемое название решателя
        """
        pass
