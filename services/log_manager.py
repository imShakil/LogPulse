import os
from typing import Dict, List
from .file_system_log_directory import FileSystemLogDirectory
from .log_directory import LogDirectory
from .logger import setup_logger

class LogManager:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing LogManager")
        
        self.directories: Dict[str, LogDirectory] = {
            'frontend': FileSystemLogDirectory(os.getenv('FRONTEND', '/home/dev/logs/frontend')),
            'backend': FileSystemLogDirectory(os.getenv('BACKEND', '/home/dev/logs/backend')),
            'admin': FileSystemLogDirectory(os.getenv('ADMIN', '/home/dev/logs/admin')),
            'nginx': FileSystemLogDirectory(os.getenv('NGINX', '/home/dev/logs/nginx')),
            'pm2': FileSystemLogDirectory(os.getenv('PM2', '/home/dev/.pm2/logs')),
        }
        
        self.app_groups = {
            'Applications': ['frontend', 'backend', 'admin'],
            'System': ['nginx', 'pm2']
        }
        self.logger.info("LogManager initialized successfully")

    def get_directory(self, app_name: str) -> LogDirectory:
        directory = self.directories.get(app_name)
        if directory:
            self.logger.debug(f"Retrieved directory for app: {app_name}")
        else:
            self.logger.warning(f"Directory not found for app: {app_name}")
        if directory is None:
            raise ValueError(f"No directory found for the specified app")
        return directory

    def get_app_groups(self) -> Dict[str, List[str]]:
        self.logger.debug("Retrieving app groups")
        return self.app_groups