import os
from .logger import setup_logger

class LogDownloader:
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.logger = setup_logger(__name__)
        
    def download_log(self):
        try:
            self.logger.info(f"Starting download of log file: {self.log_path}")
            with open(self.log_path, 'rb') as f:
                content = f.read()
            self.logger.info(f"Successfully read log file: {self.log_path}")
            return content
        except Exception as e:
            self.logger.error(f"Error downloading log file {self.log_path}: {str(e)}")
            raise