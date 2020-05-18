import threading
import time

from connection.RabbitConnection import RabbitConnection
from rpc.Server import Server


def do_job(message):
    time.sleep(5)
    print(f"SERVER: Doing shit with received stuff: {message}")
    return "SERVER: Finished doing your stuff :)"


if __name__ == "__main__":
    connection = RabbitConnection("localhost", 5672)
    server = Server(rabbit_connection=connection,
                    server_name="test_server",
                    routing_key="do_job",
                    callback=do_job)

    my_worker = threading.Thread(target=server.wait_for_job)
    my_worker.start()
    my_worker.join()
    print("Server OUT")

