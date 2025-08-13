from abc import ABC, abstractmethod

class GiveAdminPrivilegeUseCase(ABC):    
    @abstractmethod
    async def execute(self) -> None:
        pass