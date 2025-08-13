from abc import ABC, abstractmethod
from typing import List
from domain.entities import Group


class GroupDataRepository(ABC):
    """
    Интерфейс для источника данных групп
    
    Реализации могут читать данные из Google Sheets, CSV файлов, баз данных и т.д.
    """
    
    @abstractmethod
    async def get_all_groups(self) -> List[Group]:
        """
        Получить все группы из источника
        
        Returns:
            List[Group]: Список всех групп
            
        Raises:
            ExternalServiceException: Если не удалось получить данные
        """
        pass

    async def actialize_group_data(self, data: List[Group]) -> None:
        """
        Занести актуализированные данные о группах после их создания/редактирования в репозиторий
                    
        Raises:
            ExternalServiceException: Если не удалось актуализировать данные
        """
        pass
