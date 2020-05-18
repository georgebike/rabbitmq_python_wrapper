import rabbitpy

from connection.RabbitConnection import RabbitConnection


class Publisher:
    def __init__(self, rabbit_connection: RabbitConnection,
                 exchange_name: str,
                 exchange_type: str = 'topic'):

        self._rabbit_connection = rabbit_connection
        self._exchange_name = exchange_name + "_events"

        with self._rabbit_connection.connection.channel() as channel:
            self._exchange = rabbitpy.Exchange(channel=channel,
                                               name=self._exchange_name,
                                               exchange_type=exchange_type,
                                               durable=True,
                                               auto_delete=False)
            self._exchange.declare()

        print("Publisher created successfully")

    def publish(self, payload: str, routing_key: str):
        try:
            with self._rabbit_connection.connection.channel() as channel:

                message = rabbitpy.Message(channel=channel,
                                           body_value=bytes(payload, encoding='utf8'),
                                           opinionated=True)
                message.publish(exchange=self._exchange,
                                routing_key=routing_key,
                                mandatory=True,
                                immediate=False)
        except rabbitpy.exceptions.MessageReturnedException as error:
            # In in case no queue was bound to the exchange at the time of publish, create an
            # emergency queue to store the message until a consumer creates their own queue and retry publishing
            print(f"Failed to send message: {error}")

            with self._rabbit_connection.connection.channel() as _channel:
                _message = rabbitpy.Message(channel=_channel,
                                            body_value=bytes(payload + " RETRIED", encoding='utf8'),
                                            opinionated=True)

                _message.publish(exchange=self._exchange,
                                 routing_key=routing_key,
                                 mandatory=False,
                                 immediate=False)

                print("Tried to send it second time...")
