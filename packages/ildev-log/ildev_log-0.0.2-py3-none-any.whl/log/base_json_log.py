import json
import logging
import inspect
import traceback
from datetime import datetime

class BaseJsonLog:
    def __init__(self, log_file="app.log.json"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))

        self.logger.addHandler(handler)

    def log(self, level, message, exc_info=None):
        caller_frame = inspect.stack()[1]
        file_name = caller_frame.filename.split("/")[-1]
        line_number = caller_frame.lineno

        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "message": message,
            "file": file_name,
            "line": line_number,
        }
        
        if exc_info:
            log_record["error"] = {
                "type": type(exc_info).__name__,
                "message": str(exc_info),
                "traceback": traceback.format_exc()
            }

        self.logger.info(json.dumps(log_record, ensure_ascii=False))

# Example usage
if __name__ == "__main__":
    logger = BaseJsonLog()

    logger.log("info", "Application started")

    try:
        1 / 0  # Intentional error
    except Exception as e:
        logger.log("error", "An exception occurred", exc_info=e)
