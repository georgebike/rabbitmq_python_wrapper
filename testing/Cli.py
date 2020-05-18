from connection.RabbitConnection import RabbitConnection
from rpc.Client import Client


def after_job(message):
    print(f"The Server finished its work and sent me this: \n{message}")


if __name__ == "__main__":
    connection = RabbitConnection("localhost", 5672)
    client = Client(rabbit_connection=connection,
                    server_name="test_server",
                    routing_key="do_job",
                    callback=after_job)

    client.request_job("CLIENT: Please do this job")

    print("Client OUT")
