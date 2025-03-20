import contextlib
import json
import logging
from datetime import datetime, timedelta
from flask import Response, request, jsonify, send_file
from io import BytesIO
from enum import IntEnum, StrEnum, auto
from pathlib import Path
from pypomes_core import (
    APP_PREFIX, DATETIME_FORMAT_INV, TEMP_FOLDER, Mimetype,
    env_get_str, env_get_path, datetime_parse,
    validate_format_error, validate_format_errors
)
from typing import Any, Final


class LogLevel(IntEnum):
    """
    The Python log levels.
    """
    NOTSET = logging.NOTSET         # 0
    DEBUG = logging.DEBUG           # 10
    INFO = logging.INFO             # 20
    WARNING = logging.WARNING       # 30
    ERROR = logging.ERROR           # 40
    CRITICAL = logging.CRITICAL     # 50


class LogLabel(StrEnum):
    """
    Labels for the Python log levels.
    """
    NOTSET = auto()
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class LogParam(StrEnum):
    """
    The parameters for configuring the logger.
    """
    LOG_FILEMODE = auto()       # 'a' or 'w'
    LOG_FILEPATH = auto()       # a Path object
    LOG_FORMAT = auto()         # defaults to __LOG_DEFAULT_FORMAT (see below)
    LOG_LEVEL = auto()          # 'N', 'D', 'I', 'W', 'E', 'C', defaults to 'D'
    LOG_STYLE = auto()          # '{', '%', '$'
    LOG_TIMESTAMP = auto()      # defaults to '%Y-%m-%d %H:%M:%S'


VALID_GET_PARAMS: list[str] = ["log-filename", "log-level", "log-thread",
                               "log-from-datetime", "log-to-datetime", "log-last-days", "log-last-hours"]

PYPOMES_LOGGER: logging.Logger | None = None
_LOG_CONFIG_DATA: dict[LogParam, Any] = {}

__LOG_ID: Final[str] = APP_PREFIX or "_L"
__LOG_DEFAULT_FORMAT: Final[str] = ("{asctime} {levelname:1.1} {thread:5d} "
                                    "{module:20.20} {funcName:20.20} {lineno:3d} {message}")
__LOG_DEFAULT_FILEPATH: Final[Path] = Path(TEMP_FOLDER, f"{APP_PREFIX.lower()}.log")


def logging_startup(scheme: dict[str, Any] = None) -> None:
    """
    Configure/reconfigure and start/restart the log service.

    The parameters for configuring the log can be found either as environment variables, or as
    attributes in *scheme*. Default values are used, if necessary.

    :param scheme: optional log parameters and corresponding values
    """
    scheme = scheme or {}
    global PYPOMES_LOGGER

    logging_level: str = scheme.get(LogParam.LOG_LEVEL,
                                    _LOG_CONFIG_DATA.get(LogParam.LOG_LEVEL) or
                                    env_get_str(key=f"{APP_PREFIX}_LOGGING_LEVEL",
                                                def_value=LogLabel.NOTSET))[0].upper()
    logging_format: str = scheme.get(str(LogParam.LOG_FORMAT),
                                     _LOG_CONFIG_DATA.get(LogParam.LOG_FORMAT) or
                                     env_get_str(key=f"{APP_PREFIX}_LOGGING_FORMAT",
                                                 def_value=__LOG_DEFAULT_FORMAT))
    logging_style: str = scheme.get(str(LogParam.LOG_STYLE),
                                    _LOG_CONFIG_DATA.get(LogParam.LOG_STYLE) or
                                    env_get_str(key=f"{APP_PREFIX}_LOGGING_STYLE",
                                                def_value="{"))
    logging_datetime: str = scheme.get(str(LogParam.LOG_TIMESTAMP),
                                       _LOG_CONFIG_DATA.get(LogParam.LOG_TIMESTAMP) or
                                       env_get_str(key=f"{APP_PREFIX}_LOGGING_TIMESTAMP",
                                                   def_value=DATETIME_FORMAT_INV))
    logging_filemode: str = scheme.get(str(LogParam.LOG_FILEMODE),
                                       _LOG_CONFIG_DATA.get(LogParam.LOG_FILEMODE) or
                                       env_get_str(key=f"{APP_PREFIX}_LOGGING_FILEMODE",
                                                   def_value="w"))
    logging_filepath: Path = Path(scheme.get(str(LogParam.LOG_FILEPATH),
                                             _LOG_CONFIG_DATA.get(LogParam.LOG_FILEPATH) or
                                             env_get_path(key=f"{APP_PREFIX}_LOGGING_FILEPATH",
                                                          def_value=__LOG_DEFAULT_FILEPATH)))
    logging_filepath.parent.mkdir(parents=True,
                                  exist_ok=True)
    _LOG_CONFIG_DATA[LogParam.LOG_LEVEL] = logging_level
    _LOG_CONFIG_DATA[LogParam.LOG_FORMAT] = logging_format
    _LOG_CONFIG_DATA[LogParam.LOG_STYLE] = logging_style
    _LOG_CONFIG_DATA[LogParam.LOG_TIMESTAMP] = logging_datetime
    _LOG_CONFIG_DATA[LogParam.LOG_FILEMODE] = logging_filemode
    _LOG_CONFIG_DATA[LogParam.LOG_FILEPATH] = logging_filepath

    # is there a logger ?
    if PYPOMES_LOGGER:
        # yes, shut it down
        logging.shutdown()
        force_reset: bool = True
    else:
        # no
        force_reset: bool = False

    # start and configure the logger
    PYPOMES_LOGGER = logging.getLogger(name=__LOG_ID)
    # noinspection PyTypeChecker
    logging.basicConfig(filename=_LOG_CONFIG_DATA.get(LogParam.LOG_FILEPATH),
                        filemode=_LOG_CONFIG_DATA.get(LogParam.LOG_FILEMODE),
                        format=_LOG_CONFIG_DATA.get(LogParam.LOG_FORMAT),
                        datefmt=_LOG_CONFIG_DATA.get(LogParam.LOG_TIMESTAMP),
                        style=_LOG_CONFIG_DATA.get(LogParam.LOG_STYLE),
                        level=__get_level_value(_LOG_CONFIG_DATA.get(LogParam.LOG_LEVEL)),
                        force=force_reset)
    for handler in logging.root.handlers:
        handler.addFilter(filter=logging.Filter(__LOG_ID))


def logging_shutdown() -> None:
    """
    Invoke this function at shutdown.
    """
    global PYPOMES_LOGGER
    if PYPOMES_LOGGER:
        logging.shutdown()
        PYPOMES_LOGGER = None


def logging_get_entries(errors: list[str],
                        log_level: str = None,
                        log_from: datetime = None,
                        log_to: datetime = None,
                        log_thread: str = None) -> BytesIO:
    """
    Extract and return entries in the current logging file.

    Parameters specify criteria for log entry selection, and are optional.
    Intervals are inclusive (*[log_from, log_to]*).
    It is required that the current logging file be compliant with the default format,
    or that criteria for log entry selection not be specified.

    The current default format for the log is (field descriptions follow):
        {asctime} {levelname:1.1} {thread:5d} {module:20.20} {funcName:20.20} {lineno:3d} {message}
        *asctime*: timestamp, as YYYY-MM-DD hh:mm:ss
        *levelname:1.1*: first letter of the log level, in uppercase (N, D, I, W, E, C)
        *thread:5d*: first 5 digits of the thread id
        *module:20.20*: first 20 digits of the module name
        *funcName:20.20*: first 20 digits of the function name
        *lineno:3d* first 3 digits of the line number
        *message*: the log message

    :param errors: incidental error messages
    :param log_level: the logging level (defaults to all levels)
    :param log_from: the initial timestamp (defaults to unspecified)
    :param log_to: the finaL timestamp (defaults to unspecified)
    :param log_thread: the thread originating the log entries (defaults to all threads)
    :return: the logging entries meeting the specified criteria
    """
    # initialize the return variable
    result: BytesIO | None = None

    # verify whether inspecting the log entries is possible
    if _LOG_CONFIG_DATA.get(LogParam.LOG_FORMAT) != __LOG_DEFAULT_FORMAT and \
       (log_level or log_from or log_to or log_thread):
        # no, report the problem
        errors.append("It is not possible to apply level, timestamp "
                      "or thread criteria to filter log entries, "
                      "as the log format has been customized")
    else:
        # yes, proceed
        result = BytesIO()
        filepath: Path = _LOG_CONFIG_DATA.get(LogParam.LOG_FILEPATH)
        with filepath.open() as f:
            line: str = f.readline()
            while line:
                items: list[str] = line.split(sep=None,
                                              maxsplit=4)
                msg_level: int = LogLevel.CRITICAL \
                    if not log_level or len(items) < 3 \
                    else __get_level_value(log_label=items[2])
                if (not log_level or msg_level >= __get_level_value(log_level)) and \
                   (not log_thread or (len(items) > 3 and log_thread == items[3])):
                    if len(items) > 1 and (log_from or log_to):
                        timestamp: datetime = datetime_parse(f"{items[0]} {items[1]}")
                        if not (timestamp or
                                ((not log_from or timestamp >= log_from) and
                                 (not log_to or timestamp <= log_to))):
                            result.write(line.encode())
                    else:
                        result.write(line.encode())
                line = f.readline()

    return result


def logging_send_entries(scheme: dict[str, Any]) -> Response:
    """
    Retrieve from the log file, and send in response, the entries matching the criteria specified in *scheme*.

    :param scheme: the criteria for filtering the records to be returned
    :return: file containing the log entries requested
    """
    # declare the return variable
    result: Response

    # initialize the error messages list
    errors: list[str] = []

    # obtain the logging level (defaults to current level)
    log_level: str = scheme.get(str(LogParam.LOG_LEVEL),
                                _LOG_CONFIG_DATA.get(LogParam.LOG_LEVEL))
    # obtain the thread id
    log_thread: str = scheme.get("log-thread")

    # obtain the  timestamps
    log_from: datetime = datetime_parse(dt_str=scheme.get("log-from-datetime"))
    log_to: datetime = datetime_parse(dt_str=scheme.get("log-to-datetime"))

    if not log_from and not log_to:
        last_days: str = scheme.get("log-last-days", "0")
        last_hours: str = scheme.get("log-last-hours", "0")
        offset_days: int = int(last_days) if last_days.isdigit() else 0
        offset_hours: int = int(last_hours) if last_hours.isdigit() else 0
        if offset_days or offset_hours:
            log_from = datetime.now() - timedelta(days=offset_days,
                                                  hours=offset_hours)
    # retrieve the log entries
    log_entries: BytesIO = logging_get_entries(errors=errors,
                                               log_level=log_level,
                                               log_from=log_from,
                                               log_to=log_to,
                                               log_thread=log_thread)
    # errors ?
    if not errors:
        # no, return the log entries requested
        log_file = scheme.get("log-filename")
        log_entries.seek(0)
        # noinspection PyTypeChecker
        result = send_file(path_or_file=log_entries,
                           mimetype=Mimetype.TEXT.value,
                           as_attachment=log_file is not None,
                           download_name=log_file)
    else:
        # yes, report the failure
        # noinspection PyTypeChecker
        result = Response(response=json.dumps(obj={"errors": errors}),
                          status=400,
                          mimetype=Mimetype.JSON.value)

    return result


# @flask_app.route(rule="/logging",
#                  methods=["GET", "POST"])
def logging_service() -> Response:
    """
    Entry pointy for configuring and retrieving the execution log of the system.

    The *GET* operation has a set of optional criteria, used to filter the records to be returned.
    They are specified according to the pattern
    *log-filename=<string>&log-level=<debug|info|warning|error|critical>&
    log-from_datetime=YYYYMMDDhhmmss&log-to-datetime=YYYYMMDDhhmmss&log-last_days=<n>&log-last_hours=<n>>*:
        - *log-filename*: the filename for saving the downloaded the data (if omitted, browser displays the data)
        - *log-level*: the logging level of the entries (defaults to *LogLabel.DEBUG*)
        - *log-thread*: the thread originating the log entries (defaults to all threads)
        - *log-from-datetime*: the start timestamp
        - log-to-datetime*: the finish timestamp
        - *log-last-days*: how many days before current date
        - *log-last-hours*: how may hours before current time
    The *POST* operation configures and starts/restarts the logger.
    These are the optional query parameters:
        - *log-filepath*: path for the log file
        - *log-filemode*: the mode for log file opening (a- append, w- truncate)
        - *log-evel*: the logging level (*debug*, *info*, *warning*, *error*, *critical*)
        - *log-format*: the information and formats to be written to the log
        - *log-style*: the style used for building the 'log-format' parameter
        - *log-datetime*: the format for displaying the date and time (defaults to YYYY-MM-DD HH:MM:SS)
    For omitted parameters, current existing parameter values are used, or obtained from environment variables.

    :return: the requested log data, on 'GET', and the operation status, on 'POST'
    """
    # register the request
    req_query: str = request.query_string.decode()
    if PYPOMES_LOGGER:
        PYPOMES_LOGGER.info(f"Request {request.path}?{req_query}")

    # obtain the request parameters
    scheme: dict[str, Any] = {}
    # attempt to retrieve the JSON data in body
    with contextlib.suppress(Exception):
        scheme.update(request.get_json())
    # obtain parameters in URL query
    scheme.update(request.values)

    # validate the request parameters
    errors: list[str] = []
    if scheme:
        __assert_params(errors=errors,
                        method=request.method,
                        scheme=scheme)
    elif request.method == "POST":
        # 101: {}
        errors.append(validate_format_error(101,
                                            "No configuration parameters provided"))
    # run the request
    result: Response
    if errors:
        reply_err: dict = {"errors": validate_format_errors(errors=errors)}
        result = jsonify(reply_err)
        result.status_code = 400
    elif request.method == "GET":
        # retrieve the log
        result = logging_send_entries(scheme=scheme)
    else:
        # reconfigure the log
        logging_startup(scheme=scheme)
        params: dict[str, Any] = logging_get_params()
        params[LogParam.LOG_FILEPATH] = params.get(LogParam.LOG_FILEPATH).as_posix()
        reply: dict[str, Any] = {
            "status": "Log restarted",
            "criteria": params
        }
        result = jsonify(reply)

    # log the response
    if PYPOMES_LOGGER:
        PYPOMES_LOGGER.info(f"Response {request.path}?{req_query}: {result}")

    return result


def logging_get_param(key: LogParam) -> Any:
    """
    Return the current value for logging parameter *key*.

    :param key: the reference parameter
    :return: the current value of the logging parameter
    """
    return _LOG_CONFIG_DATA.get(key)


def logging_get_params() -> dict[str, Any]:
    """
    Return the current logging parameters as a *dict*.

    Note that parameter *LogParam.LOG_FILEPATH* is not serializable.

    :return: the current logging parameters
    """
    return {str(k): v for (k, v) in _LOG_CONFIG_DATA.items()}


def __assert_params(errors: list[str],
                    method: str,
                    scheme: dict) -> None:

    params: list[str] = VALID_GET_PARAMS if method == "GET" else list(map(str, LogParam))
    for key in scheme:
        if key not in params:
            # 122: Attribute is unknown or invalid in this context
            errors.append(validate_format_error(122,  # noqa: PERF401
                                                f"@{key}"))


def __get_level_value(log_label: str) -> int:
    """
    Translate the log severity *log_label* into the logging's internal severity value.

    :param log_label: the string log severity
    :return: the internal logging severity value
    """
    result: int
    match log_label:
        case str(LogLabel.DEBUG) | "D":
            result = LogLevel.DEBUG          # 10
        case str(LogLabel.INFO) | "I":
            result = LogLevel.INFO           # 20
        case str(LogLabel.WARNING) | "W":
            result = LogLevel.WARNING        # 30
        case str(LogLabel.ERROR) | "E":
            result = LogLevel.ERROR          # 40
        case str(LogLabel.CRITICAL) | "C":
            result = LogLevel.CRITICAL       # 50
        case _:
            result = LogLevel.NOTSET         # 0

    return result


# initialize the logger
logging_startup()
