import logging


class WialonLogger:
    def __init__(
        self,
        logger: logging.Logger,
        level: int = logging.DEBUG,
        format: str = "%(name)s - %(levelname)s - %(asctime)s - %(message)s",
        use_stream_handler: bool = True,
        use_file_handler: bool = False,
        filename: str = "wialon_debug.log",
    ) -> None:
        self.logger = logger
        self.logger.setLevel(level)
        formatter = logging.Formatter(format)

        if use_stream_handler and not self.logger.handlers:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        if use_file_handler and not self.logger.handlers:
            file_handler = logging.FileHandler(filename)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
