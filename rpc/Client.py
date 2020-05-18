import threading
import uuid
from typing import Callable
import rabbitpy

from connection.RabbitConnection import RabbitConnection


class Client:
    def __init__(self, rabbit_connection: RabbitConnection,
                 server_name: str,
                 routing_key: str,
                 callback: Callable = None):
        self._rabbit_connection = rabbit_connection
        self._server_name = server_name
        self._routing_key = routing_key
        self._callback = callback
        self.correlation_id = None

        with self._rabbit_connection.connection.channel() as channel:
            self._exchange_name = server_name + '_jobs'
            self._exchange = rabbitpy.Exchange(channel=channel,
                                               name=self._exchange_name,
                                               exchange_type='direct',
                                               auto_delete=False)
            self._exchange.declare()

        print(f"Client created successfully with exchange: {self._exchange.name}")

    def request_job(self, payload):
        try:
            with self._rabbit_connection.connection.channel() as channel:
                self.correlation_id = str(uuid.uuid4())
                reply_queue = rabbitpy.Queue(
                    channel=channel,
                    name='',
                    durable=True,
                    auto_delete=True,
                    message_ttl=5 * 24 * 60 * 60 * 1000  # 5 days
                )
                reply_queue.declare()
                reply_queue.bind(self._exchange, reply_queue.name)
                message = rabbitpy.Message(channel=channel,
                                           body_value=bytes(payload, encoding='utf8'),
                                           properties={
                                               'correlation_id': self.correlation_id,
                                               'reply_to': reply_queue.name,
                                           },
                                           opinionated=True)
                message.publish(exchange=self._exchange,
                                routing_key=self._routing_key,
                                mandatory=True,
                                immediate=False)
                self._consume_reply(reply_queue)
        except rabbitpy.exceptions.MessageReturnedException as error:
            # In in case no queue was bound to the exchange at the time of publish, create an
            # emergency queue to store the message until a consumer creates their own queue and retry publishing
            print(f"Failed to send message: {error}")

            with self._rabbit_connection.connection.channel() as _channel:
                _message = rabbitpy.Message(channel=_channel,
                                            body_value=bytes(payload + " RETRIED", encoding='utf8'),
                                            opinionated=True)

                _message.publish(exchange=self._exchange,
                                 routing_key=self._routing_key,
                                 mandatory=False,
                                 immediate=False)
                print("Tried to send it second time...")
                self._consume_reply(reply_queue)

    def _consume_reply(self, reply_queue):
        try:
            for message in reply_queue.consume(no_ack=True, prefetch=1):
                if (self._callback is not None
                        and message is not None
                        and self.correlation_id == message.properties['correlation_id']):
                    self._callback(message.body)
                    reply_queue.stop_consuming()
        except rabbitpy.exceptions.RemoteCancellationException:
            reply_queue.stop_consuming()
            return

