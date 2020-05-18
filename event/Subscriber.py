from typing import Callable
import rabbitpy

from connection.RabbitConnection import RabbitConnection


class Subscriber:
    def __init__(self, rabbit_connection: RabbitConnection,
                 name: str,
                 routing_key: str,
                 exchange_name: str,
                 exchange_type: str = 'topic',
                 callback: Callable = None):

        self._rabbit_connection = rabbit_connection
        self._subscriber_name = name
        self._routing_key = routing_key
        self._exchange_name = exchange_name + "_events"
        self._callback = callback

        self._queue = None

        with self._rabbit_connection.connection.channel() as channel:
            self._exchange = rabbitpy.Exchange(channel=channel,
                                               name=self._exchange_name,
                                               exchange_type=exchange_type,
                                               durable=True,
                                               auto_delete=False)
            self._exchange.declare()

        print(f"Subscriber created successfully with name {name}")

    def subscribe(self):
        """
        Subscribe method consumes messages from queue in a non-blocking manner.
        This method spawns a new thread that will consume the messages and handle them using the given callback method.

        :return:
        """
        with self._rabbit_connection.connection.channel() as channel:
            self._queue = rabbitpy.Queue(
                channel=channel,
                name=self._subscriber_name + "_queue",
                durable=True,
                message_ttl=5 * 24 * 60 * 60 * 1000  # 5 days
            )
            self._queue.declare()
            self._queue.bind(self._exchange, self._routing_key)

            self._consume()

    def unsubscribe(self):
        if self._queue is not None:
            self._queue.stop_consuming()
            self._queue = None

    def _consume(self):
        try:
            for message in self._queue.consume(no_ack=True, prefetch=1):
                if self._callback is not None and message is not None:
                    self._callback(message.body)
        except rabbitpy.exceptions.RemoteCancellationException:
            self._queue.stop_consuming()
            return


