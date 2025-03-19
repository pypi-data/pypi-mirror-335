import logging

class LoggerManager:
    def __init__(self, name: str = "Healthcare_Diagnosis", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Define log format
        log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)

        if not self.logger.hasHandlers():
            self.logger.addHandler(console_handler)

    def get_logger(self):
        """
        Returns the configured logger instance.
        """
        return self.logger
