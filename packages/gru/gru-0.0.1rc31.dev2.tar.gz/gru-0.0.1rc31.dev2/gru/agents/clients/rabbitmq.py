import base64
import os
import ssl
import threading

import pika
import logging

logger = logging.getLogger(__name__)


class RabbitMQPublisher(threading.Thread):

    CANSO_VHOST = "/canso"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.is_running = True
        self.name = "RabbitMQPublisher"

        self.host = os.environ.get("QUEUE_HOST")
        self.port = int(os.environ.get("QUEUE_PORT", 5671))
        self.username = os.getenv("QUEUE_USERNAME")
        self.password = base64.b64decode(os.getenv("QUEUE_PASSWORD")).decode()

        self.connection = self.get_connection()
        self.channel = self.connection.channel()

    def get_connection(self):
        ssl_context = ssl.create_default_context()
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            ssl_options=pika.SSLOptions(ssl_context),
            virtual_host=self.CANSO_VHOST,
        )
        return pika.BlockingConnection(parameters)

    def run(self):
        while self.is_running:
            self.connection.process_data_events(time_limit=1)

    def _publish(
        self, exchange: str, routing_key: str, message: str, correlation_id: str = None
    ):
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
                correlation_id=correlation_id,
            ),
        )

    def publish(
        self, exchange: str, routing_key: str, message: str, correlation_id: str = None
    ):
        self.connection.add_callback_threadsafe(
            lambda: self._publish(exchange, routing_key, message, correlation_id)
        )

    def stop(self):
        self.is_running = False
        if self.connection.is_open:
            # Wait until all the data events have been processed
            self.connection.process_data_events(time_limit=1)
            self.connection.close()
