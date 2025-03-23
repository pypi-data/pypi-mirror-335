import logging
from typing import Optional

from discord.utils import MISSING
from zns_logging import ZnsLogger


class Logging(ZnsLogger):
    """
    A class that extends ZnsLogger to provide flexible logging configurations.

    Args:
        reconnect (bool): Enables automatic reconnection when needed.
        log_handler (logging.Handler): The logging handler, default is determined if not provided.
        log_formatter (logging.Formatter): The log format, retrieved from the handler if not provided.
        log_level (int): The logging level.
        root_logger (bool): Specifies whether to use the root logger.
    """

    def __init__(
        self,
        reconnect: bool = True,
        log_handler: Optional[logging.Handler] = MISSING,
        log_formatter: logging.Formatter = MISSING,
        log_level: int = logging.INFO,
        root_logger: bool = False,
    ):
        super().__init__(__name__, log_level)

        self.reconnect = reconnect
        self.log_handler = log_handler
        self.log_formatter = log_formatter
        self.log_level = log_level
        self.root_logger = root_logger

        self.__init()

    def __init(self):
        if not self.log_handler:
            self.log_handler = ZnsLogger(__name__, self.log_level).handlers[0]

        if not self.log_formatter:
            self.log_formatter = self.log_handler.formatter
