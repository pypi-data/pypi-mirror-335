"""Contains the log handler to catch log"""

from __future__ import annotations

import contextlib
import logging
import re
from functools import partial
from logging import LogRecord
from typing import Callable

from .runbot_env import RunbotExcludeWarning, RunbotStepConfig

_logger = logging.getLogger("odoo_runbot.log_filter")
# 7-bit C1 ANSI sequences
ansi_escape = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)

__all__ = [
    "ExcludeWarningFilter",
    "RunbotWarningWatcherHandler",
    "get_handler",
    "start_warning_log_watcher",
]
LOGGING_FORMAT = "%(name)s:::%(message)s"


class RunbotWarningWatcherHandler(logging.Handler):
    filters: list[ExcludeWarningFilter]

    def __init__(self) -> None:
        super().__init__(logging.WARNING)
        self.set_name(type(self).__name__)
        self.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.catch_all_filter = self._get_catch_all_filter()
        self._log_emit_filter: list[ExcludeWarningFilter] = []

    def _get_catch_all_filter(self) -> ExcludeWarningFilter:
        return ExcludeWarningFilter(
            RunbotExcludeWarning(
                name="Runbot Warning catch all no filter",
                min_match=0,
                max_match=0,  # No warning is accepted
                regex=r".*",  # Every thing it's a match
            ),
        )

    def record_matchers(self) -> list[ExcludeWarningFilter]:
        return list(self._log_emit_filter)

    def emit(self, record: LogRecord) -> None:
        "Do nothing, only here to store logging."
        if record.name.startswith("odoo_runbot"):
            return
        matched = False
        formated_msg = self.format(record)
        for emit_filter in self._log_emit_filter:
            matched = matched or emit_filter.is_a_match(record, formated_msg)
        if not matched:
            self.catch_all_filter.is_a_match(record, formated_msg)

    def add_warnings(self, warnings_to_filter: list[RunbotExcludeWarning]) -> None:
        self._log_emit_filter.extend([ExcludeWarningFilter(warn_rule) for warn_rule in warnings_to_filter])

    def remove_warnings(
        self,
        warnings_to_filter: list[RunbotExcludeWarning] | None = None,
    ) -> list[ExcludeWarningFilter]:
        result: list[ExcludeWarningFilter] = []
        if not warnings_to_filter:
            result = self._log_emit_filter[:]
            self._log_emit_filter = []

        for _filter in self._log_emit_filter[:]:
            if _filter.exclude in warnings_to_filter:
                result.append(_filter)
                self._log_emit_filter.remove(_filter)

        if not self._log_emit_filter:
            result.append(self.catch_all_filter)
            self.catch_all_filter = self._get_catch_all_filter()

        return result

    def handle(self, record: LogRecord) -> None:
        if record.levelno > logging.WARNING:
            return None
        return super().handle(record)


def get_handler() -> RunbotWarningWatcherHandler | None:
    for h in logging.root.handlers:
        if isinstance(h, RunbotWarningWatcherHandler):
            return h
    return None


class ExcludeWarningFilter:
    def __init__(self, exclude: RunbotExcludeWarning) -> None:
        self.log_match: list[logging.LogRecord] = []
        self.regex = re.compile(exclude.regex, re.IGNORECASE)
        self.exclude = exclude
        _logger.info(
            "Init filter '%s' match [%s] for logger %s, between [%s, %s]",
            self.exclude.name,
            str(self.regex),
            self.exclude.logger,
            self.exclude.min_match,
            self.exclude.max_match,
        )

    def is_a_match(self, original_record: logging.LogRecord, formated_msg: str) -> bool:
        _logger.debug("OHOHOHO a new log to filter: %s", formated_msg)
        logger_name, log_msg = formated_msg.split(":::")
        if self.exclude.logger and not logger_name.startswith(self.exclude.logger):
            return False

        match = self.regex.match(log_msg)
        if not match:
            _logger.debug("Regex filter out")
            # Line don't match regex, return False to propagate to other filter
            return False
        logging.getLogger("odoo.runbot.filter").info(
            "%s matched %s for logger %s",
            self.exclude.name,
            bool(match),
            logger_name,
        )
        self.log_match.append(original_record)
        return True

    @property
    def success(self) -> bool:
        return self.exclude.min_match <= len(self.log_match) <= self.exclude.max_match

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(exclude={self.exclude!r})"

    def reset_counter(self) -> None:
        self.log_match = []


@contextlib.contextmanager
def start_warning_log_watcher(step: RunbotStepConfig) -> Callable[[], list[ExcludeWarningFilter]]:
    _logger.debug("Starting odoo logging interceptor with %s regex", len(step.log_filters))
    runbot_handler = get_handler() or RunbotWarningWatcherHandler()  # Auto registering
    runbot_handler.add_warnings(step.log_filters)
    logging.getLogger().addHandler(runbot_handler)
    yield partial(get_warning_log_watcher, step)


def get_warning_log_watcher(step: RunbotStepConfig = None) -> list[ExcludeWarningFilter]:
    runbot_handler = get_handler()
    if not runbot_handler:
        return []
    if not step:
        return runbot_handler.remove_warnings()
    return runbot_handler.remove_warnings(step.log_filters)
