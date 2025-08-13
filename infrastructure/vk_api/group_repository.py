import aiohttp
from domain.interfaces.repositories import GroupRepository
from domain.entities import Group
from domain.exceptions import (
    GroupNotFoundException, 
    ValidationException, 
    ExternalServiceException
)
from domain.services import GroupValidationService
from infrastructure.vk_api.client import VKAPIClient
from config import GROUP_CREATION_PARAMS


class VKGroupRepository(GroupRepository):
    """
    Реализация GroupRepository для работы с группами через VK API
    
    Обеспечивает создание, обновление групп и управление аватарами
    """
    
    def __init__(self, client: VKAPIClient):
        """
        Инициализация репозитория
        
        Args:
            client: Клиент VK API
        """
        self.client = client
    
    async def create_group(self, group: Group) -> str:
        """
        Создать новую группу в VK
        
        Args:
            group: Данные группы для создания
            
        Returns:
            str: VK ID созданной группы
        """
        GroupValidationService.validate_for_creation(group)
        
        try:

            # Параметры для создания группы
            params = {
                'title': group.title,
                'description': group.description,
                'screen_name': group.screen_name,
                'type': 'group',  # Тип: группа (не публичная страница)
            }
            
            # Создаем группу
            response = await self.client.call_method('groups.create', params)
            
            if not response or 'id' not in response:
                raise ExternalServiceException(
                    "VK API вернул некорректный ответ при создании группы",
                    "VK API"
                )
            
            group_id = str(response['id'])            
            return group_id
            
        except (ValidationException, ExternalServiceException):
            # Пробрасываем доменные исключения как есть
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Неожиданная ошибка при создании группы: {e}",
                "VK API"
            )
    
    async def update_group(self, group: Group) -> None:
        """
        Обновить существующую группу в VK
        
        Args:
            group: Данные группы для обновления (должен содержать vk_id)
        """
        # Валидация данных
        GroupValidationService.validate_for_update(group)
        
        vk_id = group.get_vk_id_as_int()
        if vk_id is None:
            raise ValidationException("Для обновления группы требуется корректный vk_id")
        
        try:
            # Проверяем что группа существует
            if not await self.group_exists(vk_id):
                raise GroupNotFoundException(str(vk_id))
            
            # Обновляем основную информацию, пропуская поля со знаком '-'
            params = {
                'group_id': vk_id,
                'website': f'https://vk.me/club{vk_id}',
                **GROUP_CREATION_PARAMS
            }
            
            # Добавляем поля только если они не содержат знак '-'
            if group.title.strip() != '-':
                params['title'] = group.title
            
            if group.description.strip() != '-':
                params['description'] += group.description
                
            if group.screen_name.strip() != '-':
                params['screen_name'] = group.screen_name
            # Вызываем API только если есть что обновлять
            if len(params) > 1:  # больше чем только group_id
                await self.client.call_method('groups.edit', params)
                        
            # Обновляем аватар если есть и не равен '-'
            if group.avatar_url and group.avatar_url.strip() != '-':
                try:
                    await self.set_group_avatar(vk_id, group.avatar_url)
                except Exception as e:
                    print(f"Предупреждение: не удалось обновить аватар для группы {vk_id}: {e}")
                    
        except (ValidationException, GroupNotFoundException, ExternalServiceException):
            # Пробрасываем доменные исключения как есть
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Неожиданная ошибка при обновлении группы {vk_id}: {e}",
                "VK API"
            )
    
    async def set_group_avatar(self, vk_id: int, avatar_url: str) -> None:
        """
        Установить аватар группы
        
        Args:
            vk_id: ID группы в VK
            avatar_url: URL аватарки для загрузки
        """
        try:
            # Получаем URL для загрузки фото
            upload_response = await self.client.call_method(
                'photos.getOwnerPhotoUploadServer',
                {'owner_id': f'-{vk_id}'}
            )
            
            upload_url = upload_response.get('upload_url')
            if not upload_url:
                raise ExternalServiceException(
                    "Не удалось получить URL для загрузки аватара",
                    "VK API"
                )
            
            # Скачиваем изображение
            photo_data = await self._download_image(avatar_url)
            
            # Загружаем фото на сервер VK
            upload_result = await self.client.upload_photo(upload_url, photo_data)
            
            # Сохраняем фото как аватар группы
            save_params = {
                'photo': upload_result.get('photo'),
                'hash': upload_result.get('hash'),
                'server': upload_result.get('server')
            }
            
            await self.client.call_method('photos.saveOwnerPhoto', save_params)
            
        except ExternalServiceException:
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Ошибка установки аватара для группы {vk_id}: {e}",
                "VK API"
            )
    
    async def group_exists(self, vk_id: int) -> bool:
        """
        Проверить существует ли группа в VK
        
        Args:
            vk_id: ID группы в VK
            
        Returns:
            bool: True если группа существует
        """
        try:
            response = await self.client.call_method(
                'groups.getById',
                {'group_id': vk_id}
            )
            
            return len(response) > 0
            
        except ExternalServiceException as e:
            # Если группа не найдена, это не ошибка для этого метода
            if "not found" in str(e).lower():
                return False
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Ошибка проверки существования группы {vk_id}: {e}",
                "VK API"
            )
    
    async def _download_image(self, image_url: str) -> bytes:
        """
        Скачивает изображение по URL
        
        Args:
            image_url: URL изображения
            
        Returns:
            bytes: Данные изображения
        """
        try:
            session = await self.client._get_session()
            
            async with session.get(image_url) as response:
                if response.status != 200:
                    raise ExternalServiceException(
                        f"Не удалось скачать изображение: HTTP {response.status}",
                        "HTTP"
                    )
                
                return await response.read()
                
        except aiohttp.ClientError as e:
            raise ExternalServiceException(
                f"Ошибка скачивания изображения: {e}",
                "HTTP"
            )
