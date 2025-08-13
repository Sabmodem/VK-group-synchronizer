from abc import ABC, abstractmethod

class SyncGroupsUseCase(ABC):
    """
    Use case для синхронизации групп между Google Sheets и VK
    """
    
    @abstractmethod
    async def execute(self) -> None:
        pass