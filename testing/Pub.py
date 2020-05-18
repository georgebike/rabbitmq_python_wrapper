from connection.RabbitConnection import RabbitConnection
from event.Publisher import Publisher


if __name__ == "__main__":
    connection = RabbitConnection("localhost", 5672)
    print(connection)
    publisher = Publisher(rabbit_connection=connection,
                          exchange_name="my_app")

    publisher.publish("EVENT - Status update from my_app", "my_app.status")