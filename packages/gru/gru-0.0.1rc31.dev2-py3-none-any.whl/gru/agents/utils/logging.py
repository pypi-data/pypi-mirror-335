import json
import logging
import os
from typing import Mapping

from gru.agents.clients.rabbitmq import RabbitMQPublisher
from gru.agents.utils import constants

class RabbitMQLogHandler(logging.Handler):

    ALLOWED_EXTRA_FIELDS = ["app", "correlation_id", "tenant_id"]

    def __init__(self, publisher: RabbitMQPublisher, level=logging.NOTSET):
        self.publisher = publisher
        super(RabbitMQLogHandler, self).__init__(level=level)
        self.queue = os.getenv("CANSO_INCOMING_QUEUE")

    def emit(self, record: logging.LogRecord):
        try:
            log_message = self._format(record)
            self.publisher.publish(self.queue, self.queue, log_message)
        except Exception as e:
            print(f"Exception while sending log to rabbitmq: {e}")

    def _format(self, record: logging.LogRecord) -> str:
        extra_fields = {
            k: v for k, v in record.__dict__.items() if k in self.ALLOWED_EXTRA_FIELDS
        }
        message = {
            "message_type": "log",
            "message_body": {
                "level_name": record.levelname,
                "log_message": record.getMessage(),
                "extra": extra_fields,
            },
        }

        return json.dumps(message)

    def close(self):
        self.publisher.stop()
        super().close()

def get_log_fields(correlation_id: str) -> Mapping[str, any]:
    return {
        "app": constants.APP_NAME,
        "tenant_id": constants.TENANT_ID,
        "correlation_id": correlation_id,
    }
