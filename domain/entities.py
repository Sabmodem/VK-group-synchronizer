from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass
class Group:
    """
    Доменная сущность группы ВКонтакте
    
    Представляет группу с данными из Google Sheets и информацией о синхронизации с VK
    """
    # Основные данные группы
    title: str  # Название группы
    description: str  # Описание группы
    screen_name: str  # Короткое имя для URL. UPD: Лучше оставлять пустым - vk часто дает капчу если заполнять
        
    # Управление синхронизацией
    updating: bool = False  # Флаг: нужно ли обновить группу
    
    # Интеграция с VK
    vk_id: Optional[str] = None  # ID группы в VK
    
    # Медиа
    avatar_url: Optional[str] = None  # URL аватарки для скачивания
    
    def needs_update(self) -> bool:
        """Определяет нужно ли обновлять группу в VK"""
        return self.updating
    
    def is_created_in_vk(self) -> bool:
        """Проверяет создана ли группа в VK"""
        return self.vk_id is not None and str(self.vk_id).strip() != ""
    
    def get_vk_id_as_int(self) -> Optional[int]:
        """
        Возвращает VK ID как integer для использования в API
        
        Returns:
            int: VK ID группы или None если не задан/некорректен
        """
        if not self.vk_id:
            return None
        try:
            return int(self.vk_id.strip())
        except (ValueError, AttributeError):
            return None
    
    def is_valid_for_creation(self) -> bool:
        """
        Проверяет готова ли группа для создания в VK
        
        Returns:
            bool: True если все обязательные поля заполнены
        """
        return bool(
            self.title and self.title.strip() and
            self.description and self.description.strip() and
            self.screen_name and self.screen_name.strip()
        )
    
    def is_valid_for_update(self) -> bool:
        """
        Проверяет готова ли группа для обновления в VK
        
        Returns:
            bool: True если группа создана в VK и данные корректны
        """
        return self.is_created_in_vk() and self.is_valid_for_creation()
    
    def __str__(self) -> str:
        """Читаемое представление группы"""
        status = "НОВАЯ" if not self.is_created_in_vk() else f"VK:{self.vk_id}"
        update_flag = " [ОБНОВИТЬ]" if self.needs_update() else ""
        return f"{self.title} ({status}){update_flag}"