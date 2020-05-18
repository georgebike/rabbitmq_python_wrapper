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





        # print("amqp://" + host + ":" + str(port) + "/")
        # print("amqp://192.168.0.169:5672/")
        #
        # print("amqp://" + host + str(port) + "/" == "amqp://192.168.0.169:5672/")

        # self._connection = rabbitpy.Connection("amqp://192.168.0.169:5672")