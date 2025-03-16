import os
from typing import List
from .log_directory import LogDirectory
from .logger import setup_logger
from dotenv import load_dotenv

load_dotenv()

class FileSystemLogDirectory(LogDirectory):
    def __init__(self, path: str):
        self.path = path
        self.logger = setup_logger(__name__)
        self.logger.info(f"Initialized FileSystemLogDirectory with path: {path}")
        if os.getenv('BASE_DIR'):
            self.path = str(os.getenv('BASE_DIR')) + path
    def get_logs(self) -> List[str]:
        try:
            logs = [f for f in os.listdir(self.path) if f.endswith('.log')]
            self.logger.debug(f"Found {len(logs)} log files in {self.path}")
            return logs
        except Exception as e:
            self.logger.error(f"Error getting logs from {self.path}: {str(e)}")
            raise

    def get_log_path(self, log_file: str) -> str:
        full_path = os.path.join(self.path, log_file)
        self.logger.debug(f"Generated full path: {full_path}")
        return full_path