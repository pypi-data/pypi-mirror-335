from abc import ABC, abstractmethod

class BaseTarget(ABC):
    @abstractmethod
    def write(self, data: dict, path: str) -> None:
        """Writes data to the target format"""
        pass

    @staticmethod
    @abstractmethod
    def accepts_type(data_type: str) -> bool:
        """Return True if this target accepts the given type"""
        pass
