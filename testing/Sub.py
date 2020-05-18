import threading

from connection.RabbitConnection import RabbitConnection
from event.Subscriber import Subscriber


def handle_event(message):
    print(f"Subscriber's callback was called. The event body is: \n{message.decode('utf-8')}")


if __name__ == "__main__":
    connection = RabbitConnection("localhost", 5672)
    print(connection)
    sub = Subscriber(rabbit_connection=connection,
                     name="Happy_subscriber",
                     routing_key="my_app.status",
                     exchange_name="my_app",
                     callback=handle_event
                     )
    threading.Thread(target=sub.subscribe).start()



