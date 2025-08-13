from domain.entities import Group
from domain.exceptions import ExternalServiceException
from domain.interfaces import GroupSettingsInteractor as IGroupSettingsInteractor
from domain.dto import SetGroupAdminDto
from infrastructure.vk_api.client import VKAPIClient

class GroupSettingsInteractor(IGroupSettingsInteractor):
    def __init__(
        self,
        client: VKAPIClient
    ):
        self.client = client

    async def join_group(self, group: Group) -> None:
        '''
        Вступить в группу вк
        '''
        
        try:
            params = {
                'group_id': group.vk_id
            }
            await self.client.call_method('groups.join', params)                        
        except ExternalServiceException:
            # Пробрасываем доменные исключения как есть
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Неожиданная ошибка при вступлении в группу: {e}",
                "VK API"
            )

    async def set_group_admin(self, data: SetGroupAdminDto) -> None:
        '''
        Поставить юзера админом в группе
        '''

        try:            
            await self.client.call_method('groups.editManager', params=data.to_json())                        
        except ExternalServiceException:
            # Пробрасываем доменные исключения как есть
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Неожиданная ошибка при изменении прав доступа на группу: {e}",
                "VK API"
            )