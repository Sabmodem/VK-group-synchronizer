from abc import ABC, abstractmethod
from domain.entities import Group


class GroupRepository(ABC):
    """
    Интерфейс для управления группами в VK
    
    Инкапсулирует операции создания и обновления групп через VK API
    """
    
    @abstractmethod
    async def create_group(self, group: Group) -> str:
        """
        Создать новую группу в VK
        
        Args:
            group: Данные группы для создания
            
        Returns:
            str: VK ID созданной группы
            
        Raises:
            ValidationException: Если данные группы некорректны
            ExternalServiceException: Если произошла ошибка VK API
            RateLimitException: Если превышен лимит запросов
            CaptchaRequiredException: Если требуется решение капчи
        """
        pass
    
    @abstractmethod
    async def update_group(self, group: Group) -> None:
        """
        Обновить существующую группу в VK
        
        Args:
            group: Данные группы для обновления (должен содержать vk_id)
            
        Raises:
            GroupNotFoundException: Если группа не найдена в VK
            ValidationException: Если данные группы некорректны
            ExternalServiceException: Если произошла ошибка VK API
            RateLimitException: Если превышен лимит запросов
            CaptchaRequiredException: Если требуется решение капчи
        """
        pass
    
    @abstractmethod
    async def set_group_avatar(self, vk_id: int, avatar_url: str) -> None:
        """
        Установить аватар группы
        
        Args:
            vk_id: ID группы в VK
            avatar_url: URL аватарки для загрузки
            
        Raises:
            GroupNotFoundException: Если группа не найдена в VK
            ExternalServiceException: Если произошла ошибка VK API или загрузки аватара
        """
        pass
    
    @abstractmethod
    async def group_exists(self, vk_id: int) -> bool:
        """
        Проверить существует ли группа в VK
        
        Args:
            vk_id: ID группы в VK
            
        Returns:
            bool: True если группа существует
            
        Raises:
            ExternalServiceException: Если произошла ошибка VK API
        """
        pass
