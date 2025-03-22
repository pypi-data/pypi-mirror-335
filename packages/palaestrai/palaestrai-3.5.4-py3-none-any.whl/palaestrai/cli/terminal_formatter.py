from __future__ import annotations
from typing import TYPE_CHECKING

import os
import sys
import time
import logging
import functools

if TYPE_CHECKING:
    from logging import LogRecord


class TerminalFormatter(logging.Formatter):
    RESET_SEQ = "\033[0m"
    BOLD_SEQ = "\033[1m"
    DIM_SEQ = "\033[2m"
    BLINKING_SEQ = "\033[5m"
    BLACK_SEQ = "\033[30m"
    RED_SEQ = "\033[31m"
    GREEN_SEQ = "\033[32m"
    YELLOW_SEQ = "\033[33m"
    BRIGHT_RED_SEQ = "\033[91m"
    BRIGHT_GREEN_SEQ = "\033[92m"
    BRIGHT_YELLOW_SEQ = "\033[93m"
    BRIGHT_WHITE_SEQ = "\033[97m"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @functools.cached_property
    def _isa_tty(self) -> bool:
        return sys.stdout.isatty()

    @functools.cached_property
    def _has_dark_bg(self) -> bool:
        if os.environ.get("COLORFGBG", None):
            parts = os.environ["COLORFGBG"].split(";")
            try:
                last_number = int(parts[-1])
                if 0 <= last_number <= 6 or last_number == 8:
                    return True
                else:
                    return False
            except ValueError:  # not an integer?
                pass
        return True

    @functools.cached_property
    def _separator(self):
        if not self._isa_tty:
            return "|"
        if self._has_dark_bg:
            return (
                f"{TerminalFormatter.BOLD_SEQ}"
                f"{TerminalFormatter.BRIGHT_WHITE_SEQ}|"
                f"{TerminalFormatter.RESET_SEQ}"
            )
        return (
            f"{TerminalFormatter.BOLD_SEQ}"
            f"{TerminalFormatter.BLACK_SEQ}|"
            f"{TerminalFormatter.RESET_SEQ}"
        )

    @functools.cached_property
    def _color_seq(self):
        color_seq = {"BLACK": TerminalFormatter.BLACK_SEQ}
        if self._has_dark_bg:
            color_seq.update(
                {
                    "GREEN": TerminalFormatter.BRIGHT_GREEN_SEQ,
                    "YELLOW": TerminalFormatter.BRIGHT_YELLOW_SEQ,
                    "RED": TerminalFormatter.BRIGHT_RED_SEQ,
                }
            )
        else:
            color_seq.update(
                {
                    "GREEN": TerminalFormatter.GREEN_SEQ,
                    "YELLOW": TerminalFormatter.YELLOW_SEQ,
                    "READ": TerminalFormatter.RED_SEQ,
                }
            )
        return color_seq

    def _format_loglevel(self, record: logging.LogRecord) -> str:
        if not self._isa_tty:
            return logging.getLevelName(record.levelno)

        color_seq = ""
        if self._has_dark_bg:
            color_seq = {
                logging.NOTSET: "",
                logging.INFO: TerminalFormatter.BRIGHT_GREEN_SEQ,
                logging.WARNING: TerminalFormatter.BRIGHT_YELLOW_SEQ,
                logging.WARN: TerminalFormatter.BRIGHT_YELLOW_SEQ,
                logging.ERROR: TerminalFormatter.BRIGHT_RED_SEQ,
                logging.CRITICAL: f"{TerminalFormatter.BLINKING_SEQ}"
                f"{TerminalFormatter.BRIGHT_RED_SEQ}",
            }.get(record.levelno, "")
        else:
            color_seq = {
                logging.NOTSET: "",
                logging.INFO: TerminalFormatter.GREEN_SEQ,
                logging.WARNING: TerminalFormatter.YELLOW_SEQ,
                logging.WARN: TerminalFormatter.YELLOW_SEQ,
                logging.ERROR: TerminalFormatter.RED_SEQ,
                logging.CRITICAL: f"{TerminalFormatter.BLINKING_SEQ}"
                f"{TerminalFormatter.RED_SEQ}",
            }.get(record.levelno, "")
        return "{c}{l:<8}".format(
            c=color_seq, l=logging.getLevelName(record.levelno)
        )

    def _format_message(self, record: logging.LogRecord) -> str:
        if not self._isa_tty:
            return record.getMessage()
        if record.levelno == logging.DEBUG:
            return (
                f"{TerminalFormatter.DIM_SEQ}{record.getMessage()}"
                f" @ {record.filename}:{record.lineno}"
            )
        return record.getMessage()

    def format(self, record: logging.LogRecord) -> str:
        t = time.localtime(record.created)
        t_str = time.strftime("%Y-%m-%d %H:%M:%S", t)
        return (
            "{reset}{t_str},{t_msecs:3.0f} {sep} {level}{reset} "
            "{sep} {msg}{reset}"
        ).format(
            reset=TerminalFormatter.RESET_SEQ,
            t_str=t_str,
            t_msecs=record.msecs,
            sep=self._separator,
            level=self._format_loglevel(record),
            msg=self._format_message(record),
        )
