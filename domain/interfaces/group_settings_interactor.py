from abc import ABC, abstractmethod
from domain.entities import Group
from domain.dto import SetGroupAdminDto


class GroupSettingsInteractor(ABC):
    """
    Интерфейс для взаимодействия с группами в VK
    
    Инкапсулирует логику взаимодействия с группами через VK API. Например, вступить в группу, назначить админа и тд
    """
    
    @abstractmethod
    async def join_group(self, group: Group) -> None:
        '''
        Вступить в группу вк
        '''
        pass

    @abstractmethod
    async def set_group_admin(self, group: Group, data: SetGroupAdminDto) -> None:
        '''
        Поставить юзера админом в группе
        '''
        pass