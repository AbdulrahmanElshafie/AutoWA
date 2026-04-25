import logging
import os
import traceback
import functools
import time
import json
from datetime import datetime

# --------------------------------------------------
# Setup logging folder
# --------------------------------------------------
# Create a "logs" folder if it does not exist to store log files.
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# --------------------------------------------------
# Central Logger
# --------------------------------------------------
# Create a single logger instance to be used throughout the application.
logger = logging.getLogger("MainLogger")
logger.setLevel(logging.DEBUG) # Capture all levels; handlers will filter
logger.propagate = False  # Prevent duplication in root logger

# --------------------------------------------------
# Formatters
# --------------------------------------------------
# Defines the format for log messages: timestamp | level | message
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --------------------------------------------------
# File handlers
# --------------------------------------------------
# Handler for INFO and higher logs
info_handler = logging.FileHandler(os.path.join(LOG_DIR, "info.log"), encoding="utf-8")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

# Handler for ERROR logs only
error_handler = logging.FileHandler(os.path.join(LOG_DIR, "error.log"), encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Add handlers to the logger if not already added
if not logger.handlers:
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

# --------------------------------------------------
# Console handler (disabled by default)
# --------------------------------------------------
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Default console level
console_handler.setFormatter(formatter)

# Flag to track if console logging is enabled
_console_enabled = False

def enable_console_logging(level=logging.INFO):
    """
    Enable logging output to the console.

    Parameters:
    - level (int): Logging level for console output (e.g., logging.INFO, logging.DEBUG)

    Usage:
    enable_console_logging(logging.DEBUG)
    """
    global _console_enabled
    if not _console_enabled:
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
        _console_enabled = True

def disable_console_logging():
    """
    Disable logging output to the console.

    Usage:
    disable_console_logging()
    """
    global _console_enabled
    if _console_enabled:
        logger.removeHandler(console_handler)
        _console_enabled = False

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _safe_repr(obj, max_len=500):
    """
    Safely represent an object as a string, truncating if too long.

    Parameters:
    - obj (any): Object to represent
    - max_len (int): Maximum length of string representation

    Returns:
    - str: String representation of the object (truncated if necessary)

    Logic:
    - Uses repr() to generate a detailed string
    - Truncates strings exceeding max_len to prevent excessively long logs
    - Handles objects that may raise exceptions during repr()
    """
    try:
        text = repr(obj)
        return text if len(text) <= max_len else text[:max_len] + "...<truncated>"
    except Exception:
        return "<unreprable>"


# --------------------------------------------------
# Logging functions
# --------------------------------------------------
def log_info(msg: str, **kwargs):
    """
    Log an informational message with optional key-value details.

    Parameters:
    - msg (str): Main message to log
    - kwargs: Optional key-value pairs to include in the log

    Logic:
    - If additional details are provided via kwargs, they are appended to the message
    - Uses _safe_repr to ensure objects are safely represented
    """
    if kwargs:
        details = " | ".join(f"{k}={_safe_repr(v)}" for k, v in kwargs.items())
        msg = f"{msg} | {details}"
    logger.info(msg)


def log_error(msg: str, exc: Exception | None = None):
    """
    Log an error message, optionally including the exception traceback.

    Parameters:
    - msg (str): Main error message
    - exc (Exception | None): Optional exception to log

    Logic:
    - If an exception is provided, formats the full traceback and appends it to the message
    - Writes the error to the error log file
    """
    if exc:
        trace = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        msg = f"{msg}\n{trace}"
    logger.error(msg)


# --------------------------------------------------
# Decorator
# --------------------------------------------------
def log_function(func):
    """
    Decorator to automatically log function calls, arguments, return values,
    execution time, and exceptions.

    Parameters:
    - func (callable): The function to wrap

    Returns:
    - callable: Wrapped function with logging

    Logic:
    1. Logs function entry and all arguments
    2. Executes the function and logs its return value and duration
    3. If an exception occurs, logs the full traceback and duration, then re-raises
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        # Log function call and arguments
        log_info(
            f"CALL: {func.__name__}",
            args=args,
            kwargs=kwargs
        )

        try:
            # Execute the original function
            result = func(*args, **kwargs)
            duration = round(time.perf_counter() - start, 4)

            # Log return value and execution duration
            log_info(
                f"RETURN: {func.__name__}",
                result=result,
                duration=f"{duration}s"
            )
            return result

        except Exception as exc:
            # Log exception with traceback and duration
            duration = round(time.perf_counter() - start, 4)
            log_error(
                f"EXCEPTION in {func.__name__} | duration={duration}s",
                exc=exc
            )
            raise

    return wrapper

def log_execution(action: str, status: str, duration: float = 0.0, error_type: str = None, session_id: str = None):
    """
    Log an entry to the JSONL execution log file.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "status": status,
        "duration": duration,
        "error_type": error_type,
        "session_id": session_id
    }
    with open(os.path.join(LOG_DIR, "execution_log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
