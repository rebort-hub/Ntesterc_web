import logging


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return super().format(record)
