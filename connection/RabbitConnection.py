import rabbitpy


class RabbitConnection:
    def __init__(self, host: str, port: int):
        self._connection = rabbitpy.Connection("amqp://" + host + ":" + str(port) + "/")
        print("RabbitConnection - Connection created successfully")

    @property
    def connection(self):
        return self._connection

    def close_connection(self):
        self._connection.close()
