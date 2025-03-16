import time
import os
from .logger import setup_logger

class LogStreamReader:
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.logger = setup_logger(__name__)
        self.logger.info(f"Initialized LogStreamReader for: {log_path}")

    def generate_stream(self):
        try:
            with open(self.log_path, 'rb') as f:
                self.logger.debug(f"Started streaming file: {self.log_path}")
                f.seek(0, os.SEEK_END)
                lines = []
                block_size = 1024
                file_size = f.tell()
                seek_offset = 0

                while len(lines) < 100 and file_size > 0:
                    seek_offset = min(file_size, seek_offset + block_size)
                    f.seek(-seek_offset, os.SEEK_END)
                    data = f.read(seek_offset)
                    lines = data.splitlines()
                    file_size -= seek_offset

                self.logger.debug(f"Initial read complete, found {len(lines)} lines")
                decoded_lines = [line.decode('utf-8', errors='replace') for line in lines[-100:]]
                for line in decoded_lines:
                    yield f'data: {line}\n\n'

                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    decoded_line = line.decode('utf-8', errors='replace').rstrip()
                    yield f'data: {decoded_line}\n\n'
        except Exception as e:
            self.logger.error(f"Error streaming log file {self.log_path}: {str(e)}")
            raise