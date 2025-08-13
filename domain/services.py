from typing import List
from domain.entities import Group
from domain.exceptions import ValidationException, InvalidGroupDataException


class GroupValidationService:
    """
    Доменный сервис для валидации групп
    
    Содержит бизнес-правила валидации данных групп
    """
    
    @staticmethod
    def validate_for_creation(group: Group) -> None:
        """
        Валидация группы перед созданием в VK
        
        Args:
            group: Группа для валидации
            
        Raises:
            InvalidGroupDataException: Если данные некорректны
        """
        errors = []
        
        # Проверяем обязательные поля
        if not group.title or not group.title.strip() or group.title.strip() == '-':
            errors.append("Название группы обязательно")
        elif len(group.title.strip()) < 2:
            errors.append("Название группы должно содержать минимум 2 символа")
        elif len(group.title.strip()) > 100:
            errors.append("Название группы не должно превышать 100 символов")
            
        if not group.description or not group.description.strip() or group.description.strip() == '-':
            errors.append("Описание группы обязательно")
        elif len(group.description.strip()) > 5000:
            errors.append("Описание группы не должно превышать 5000 символов")
            
        if not group.screen_name or not group.screen_name.strip():
            errors.append("Короткое имя (screen_name) обязательно")
        else:
            screen_name = group.screen_name.strip().lower()
            if not GroupValidationService._is_valid_screen_name(screen_name):
                errors.append("Короткое имя может содержать только буквы, цифры и подчеркивания")
            elif len(screen_name) > 50:
                errors.append("Короткое имя не должно превышать 50 символов")
                
        # Проверяем опциональные поля
        if group.avatar_url and not GroupValidationService._is_valid_url(group.avatar_url):
            errors.append("Некорректный URL аватарки")
        
        if errors:
            raise InvalidGroupDataException(f"Ошибки валидации: {'; '.join(errors)}")
    
    @staticmethod
    def validate_for_update(group: Group) -> None:
        """
        Валидация группы перед обновлением в VK
        
        Args:
            group: Группа для валидации
            
        Raises:
            InvalidGroupDataException: Если данные некорректны
        """
        errors = []
        
        # Проверяем обязательные поля, учитывая что '-' означает "не обновлять"
        if not group.title or not group.title.strip():
            errors.append("Название группы обязательно")
        elif group.title.strip() != '-':
            # Проверяем валидность только если поле не пропускается
            if len(group.title.strip()) < 2:
                errors.append("Название группы должно содержать минимум 2 символа")
            elif len(group.title.strip()) > 100:
                errors.append("Название группы не должно превышать 100 символов")
            
        if not group.description or not group.description.strip():
            errors.append("Описание группы обязательно")
        elif group.description.strip() != '-':
            if len(group.description.strip()) > 5000:
                errors.append("Описание группы не должно превышать 5000 символов")
            
        if not group.screen_name or not group.screen_name.strip():
            errors.append("Короткое имя (screen_name) обязательно")
        elif group.screen_name.strip() != '-':
            screen_name = group.screen_name.strip().lower()
            if not GroupValidationService._is_valid_screen_name(screen_name):
                errors.append("Короткое имя может содержать только буквы, цифры и подчеркивания")
            elif len(screen_name) < 3:
                errors.append("Короткое имя должно содержать минимум 3 символа")
            elif len(screen_name) > 50:
                errors.append("Короткое имя не должно превышать 50 символов")
                
        # Проверяем опциональные поля
        if group.avatar_url and group.avatar_url.strip() != '-' and not GroupValidationService._is_valid_url(group.avatar_url):
            errors.append("Некорректный URL аватарки")
        
        # Дополнительно проверяем наличие VK ID
        if not group.is_created_in_vk():
            errors.append("Для обновления группа должна быть создана в VK (vk_id обязателен)")
        else:
            vk_id = group.get_vk_id_as_int()
            if vk_id is None or vk_id <= 0:
                errors.append("Некорректный VK ID группы")
        
        if errors:
            raise InvalidGroupDataException(f"Ошибки валидации: {'; '.join(errors)}")
    
    @staticmethod
    def _is_valid_screen_name(screen_name: str) -> bool:
        """Проверяет корректность короткого имени"""
        if not screen_name:
            return False
        
        # Только буквы, цифры и подчеркивания
        allowed_chars = set('-abcdefghijklmnopqrstuvwxyz0123456789_')
        return all(c in allowed_chars for c in screen_name.lower())
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Базовая проверка URL"""
        if not url:
            return False
        return url.startswith(('http://', 'https://')) and len(url) > 10


class GroupSyncService:
    """
    Доменный сервис для логики синхронизации групп
    """
    
    @staticmethod
    def filter_groups_for_processing(groups: List[Group], max_count: int = None) -> List[Group]:
        """
        Фильтрует и сортирует группы для обработки
        
        Args:
            groups: Исходный список групп
            max_count: Максимальное количество групп для возврата
            
        Returns:
            List[Group]: Отфильтрованный список групп
        """
        # Берем только группы требующие обновления
        groups_to_process = [g for g in groups if g.needs_update()]
        
        # Сортируем: сначала новые группы (без VK ID), потом обновления
        groups_to_process.sort(key=lambda g: (g.is_created_in_vk(), g.title))
        
        # Ограничиваем количество если задано
        if max_count and max_count > 0:
            groups_to_process = groups_to_process[:max_count]
        
        return groups_to_process
    
    @staticmethod
    def group_groups_by_account(groups: List[Group]) -> dict[str, List[Group]]:
        """
        Группирует группы по аккаунтам
        
        Args:
            groups: Список групп
            
        Returns:
            dict: Словарь {account: [Group, ...]}
        """
        result = {}
        for group in groups:
            account = group.account
            if account not in result:
                result[account] = []
            result[account].append(group)
        return result
