import asyncio
from typing import Optional
from infrastructure.interfaces.captcha_solver import CaptchaSolver
from urllib.parse import unquote


class ConsoleCaptchaSolver(CaptchaSolver):
    """
    Интерактивное решение капчи через консоль
    
    Показывает пользователю ссылку на изображение капчи и запрашивает
    ввод текста через консоль
    """
    
    def __init__(self, max_attempts: int = 3):
        """
        Инициализация решателя капчи
        
        Args:
            max_attempts: Максимальное количество попыток ввода
        """
        self.max_attempts = max_attempts
    
    async def solve_captcha(self, captcha_sid: str, captcha_img: str) -> Optional[str]:
        """
        Решает капчу через интерактивный ввод в консоли
        
        Args:
            captcha_sid: ID капчи для повторного запроса
            captcha_img: URL изображения капчи
            
        Returns:
            str: Введенный пользователем текст или None при отмене
        """
        print("\n" + "="*60)
        print("🛡️  ТРЕБУЕТСЯ РЕШЕНИЕ КАПЧИ VK API")
        print("="*60)
        print(f"Откройте ссылку в браузере (raw link): {captcha_img}")
        print(f"Откройте ссылку в браузере (decoded link): {unquote(captcha_img)}")
        print(f"Captcha SID: {captcha_sid}")
        print("="*60)
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                print(f"\n📝 Попытка {attempt} из {self.max_attempts}")
                print("Введите текст с изображения капчи:")
                print("(или нажмите Enter чтобы пропустить, 'q' для выхода)")
                
                captcha_text = await self._get_user_input()
                
                if captcha_text is None:
                    print("⏭️  Капча пропущена пользователем")
                    return None
                
                if captcha_text.lower() == 'q':
                    print("🚪 Выход по запросу пользователя")
                    return None
                
                if captcha_text.strip():
                    print(f"✅ Получен текст капчи: {captcha_text}")
                    return captcha_text.strip()
                else:
                    print("⚠️  Введен пустой текст, повторите ввод")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Решение капчи прервано пользователем")
                return None
            except Exception as e:
                print(f"❌ Ошибка ввода: {e}")
                continue
        
        print(f"\n❌ Исчерпано максимальное количество попыток ({self.max_attempts})")
        return None
    
    async def _get_user_input(self) -> Optional[str]:
        """
        Получает ввод пользователя асинхронно
        
        Returns:
            str: Введенный текст или None при пустом вводе
        """
        loop = asyncio.get_event_loop()
        
        def _input():
            try:
                return input("Капча: ").strip()
            except EOFError:
                return None
        
        result = await loop.run_in_executor(None, _input)
        return result if result else None
    
    def get_solver_name(self) -> str:
        """Возвращает название решателя"""
        return "Интерактивный решатель капчи (консоль)"
    
    def print_instructions(self) -> None:
        """Выводит инструкции по решению капчи"""
        print("\n💡 Инструкции по решению капчи:")
        print("  1. Скопируйте ссылку на изображение")
        print("  2. Откройте ее в браузере")
        print("  3. Введите текст с изображения в консоль")
        print("  4. Нажмите Enter для подтверждения")
        print("  5. При ошибке процесс повторится автоматически")