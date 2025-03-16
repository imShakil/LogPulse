from abc import ABC, abstractmethod
from typing import List

class LogDirectory(ABC):
    @abstractmethod
    def get_logs(self) -> List[str]:
        pass

    @abstractmethod
    def get_log_path(self, log_file: str) -> str:
        pass