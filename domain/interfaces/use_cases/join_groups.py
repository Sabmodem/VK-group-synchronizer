from abc import ABC, abstractmethod

class JoinGroupsUseCase(ABC):    
    @abstractmethod
    async def execute(self) -> None:
        pass