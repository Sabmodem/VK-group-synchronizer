from abc import ABC, abstractmethod

class CreateGroupsUseCase(ABC):
    @abstractmethod
    async def execute(self) -> None:
        pass