import datetime
import json
import logging
import time
from typing import Optional, Any, Dict

class XenitJsonFormatter(logging.Formatter):
    def __init__(
        self, 
        component: str, 
        additional_keys: dict[str,str] = {}, 
        fmt: Optional[str] = None, 
        datefmt: Optional[str] = None, 
        style: str = "%", 
        validate: bool = True, 
        defaults: Optional[Dict[str, Any]] = None
    ):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        self.component = component
        self.additional_keys = additional_keys

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": time.time(),
            "type": "application",
            "component": self.component,
            "time": datetime.datetime.now(datetime.UTC).isoformat(
                sep=" ", timespec="milliseconds"
            ),
            "shortMessage": record.getMessage() if record.getMessage() else "",
            "loggerName": record.name,
            "severity": record.levelname,
            "thread": record.threadName,
            "fullMessage": self._get_full_message(record),
            "level": record.levelno,
            "sourceClassName": record.pathname,
            "sourceLineNumber": record.lineno,
            "sourceMethodName": record.funcName,
        }
        
        # Add additional keys dynamically
        for additional_key, additional_value in self.additional_keys.items():
            log_entry[additional_key] = getattr(record, additional_value, None)
        
        return json.dumps(log_entry, ensure_ascii=False)
    
    def _get_full_message(self, record: logging.LogRecord) -> str:
        """
        Safely extract full error message
        """
        if record.exc_info:
            return self.formatException(record.exc_info)
        return record.exc_text or ""

def setup_json_logging(
    component: str = "cg-extension", 
    additional_keys: dict[str,str] = {}, 
    log_level: int = logging.DEBUG
) -> logging.Logger:
    """
    Setup JSON logging with a single logger
    
    Args:
        component (str): Name of the component for logging
        additional_keys (dict[str, str]): Additional keys to include in log. The key is the key in the json logline, the value is the value of in the extra field for the logging lib.
        log_level (int): Logging level (default: DEBUG)
    
    Returns:
        logging.Logger: Configured logger
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to prevent duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    
    # Create JSON formatter
    formatter = XenitJsonFormatter(
        component=component, 
        additional_keys=additional_keys
    )
    
    # Add formatter to handler
    ch.setFormatter(formatter)
    
    # Add handler to logger
    root_logger.addHandler(ch)