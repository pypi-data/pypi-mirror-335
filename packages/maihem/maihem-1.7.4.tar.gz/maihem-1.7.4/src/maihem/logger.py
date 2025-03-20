import sys
import os
from loguru import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Logger

from loguru._logger import Logger


def add_default_logger(
    logger: Logger, level: str = "DEBUG", show_details: bool = False
):
    logger.remove()

    def format_message(record):
        # Add a relative pathname to 'extra', but do not overwrite existing keys
        record["extra"][
            "pathname"
        ] = f"{os.path.relpath(record['file'].path)}:{record['line']}"

        # Base format string
        base_format = (
            "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> - "
            "<level>{level}</level> - {message}"
        )

        if show_details:
            base_format += " - <dim>{extra[pathname]}</dim>"

        # Add any additional 'extra' fields dynamically
        for key, value in record["extra"].items():
            if key == "pathname":  # Skip 'pathname' since it's already included
                continue
            if value:  # Only include non-empty values
                base_format += f" - <dim>{key}:{{extra[{key}]}}</dim>"

        # Include exception details if present
        if record["exception"]:
            base_format += "\n<red>{exception}</red>"

        base_format += "\n"
        return base_format

    logger.add(
        sys.stdout,
        colorize=True,
        format=format_message,
        level=level,
        backtrace=True,
        diagnose=False,
    )


def get_logger() -> Logger:
    return logger
