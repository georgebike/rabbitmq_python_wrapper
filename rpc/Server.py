from typing import Callable
import rabbitpy

from connection.RabbitConnection import RabbitConnection


class Server:
    def __init__(self, rabbit_connection: RabbitConnection,
                 server_name: str,
                 routing_key: str,
                 callback: Callable = None):
        self._rabbit_connection = rabbit_connection
        self._server_name = server_name
        self._routing_key = routing_key
        self._callback = callback

        self._queue = None

        self._exchange_name = server_name + '_jobs'

        with self._rabbit_connection.connection.channel() as channel:
            self._exchange = rabbitpy.Exchange(channel=channel,
                                               name=self._exchange_name,
                                               exchange_type='direct',
                                               auto_delete=False)
            self._exchange.declare()

        print(f"Server created successfully with name {self._server_name} and exchange: {self._exchange.name}")

    def wait_for_job(self):
        with self._rabbit_connection.connection.channel() as channel:
            self._queue = rabbitpy.Queue(
                channel=channel,
                name=self._server_name + "_" + self._routing_key + "_queue",
                durable=True,
                message_ttl=5 * 24 * 60 * 60 * 1000  # 5 days
            )
            self._queue.declare()
            self._queue.bind(self._exchange, self._routing_key)

            self._consume(channel)

    def _consume(self, channel):
        try:
            for message in self._queue.consume(prefetch=1):
                if self._callback is not None and message is not None:
                    _job_result = self._callback(message.body)
                    message.ack()
                    _return_message = rabbitpy.Message(channel=channel,
                                                       body_value=bytes(_job_result, encoding='utf8'),
                                                       properties={'correlation_id': message.properties['correlation_id']},
                                                       opinionated=True)
                    _return_message.publish(exchange=self._exchange,
                                            routing_key=message.properties['reply_to'],
                                            mandatory=False,
                                            immediate=False)
        except rabbitpy.exceptions.RemoteCancellationException:
            self._queue.stop_consuming()
            return
