from abc import ABC, abstractmethod

class BaseSource(ABC):
    @abstractmethod
    def extract(self, path: str) -> dict:
        """Extracts raw data from the file"""
        pass

    @classmethod
    def supported_extensions(cls):
        """Return a list of supported file extensions for this source"""
        return []

    @classmethod
    def data_type(cls):
        """Return the data type that this source extracts"""
        return None