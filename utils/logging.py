import logging
import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.datetime.now().isoformat()
            log_record['timestamp'] = now

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.FileHandler(filename="events.jsonl")

def set_file(path: str):
    logHandler = logging.FileHandler(filename=path)
    logHandler.setLevel(logging.INFO)
    formatter = CustomJsonFormatter()
    logHandler.setFormatter(formatter)
    logger.handlers = [logHandler, ]

set_file("events.jsonl")
