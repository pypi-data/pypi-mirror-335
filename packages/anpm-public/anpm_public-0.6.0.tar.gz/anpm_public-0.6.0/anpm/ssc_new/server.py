from socket import *

from threading import Thread
from datetime import datetime
from json import loads, dumps

try: from .shared import *
except ImportError: from shared import *


class Server(socket):
    def __init__(self):
        self.running: bool = False
        self.aliveThread: Thread | None = None
        self.activeClients: list[tuple[socket, tuple[str, int]]] = []

        super().__init__(AF_INET, SOCK_STREAM)

    def start(self, port: int, client_limit: int = 5):
        super().__init__(AF_INET, SOCK_STREAM)
        self.bind(("0.0.0.0", port))
        self.listen(client_limit)

        self.running = True

        self.aliveThread = Thread(target=self.while_alive)
        self.aliveThread.start()

        log(f"Started started on {ip_str(get_ip(), port)}...")

    def stop(self):
        self.running = False

        [cs.shutdown(SHUT_RDWR) for cs, _ in self.activeClients]

        self.activeClients.clear()

        self.close()

        log(f"Stopped server!")

    def while_alive(self):
        while self.running:
            try: Thread(target=self.handle_client, args=self.accept(), daemon=True).start()

            except OSError as e:
                if e.errno == 10038: ...
                else: raise e

    def handle_client(self, c_socket: socket, c_address: tuple[str, int]):
        self.activeClients.append((c_socket, c_address))

        log(f"{ip_str(*c_address)} connected!")

        while self.running:
            try:
                messages = c_socket.recv(1024)
                messages = decrypt_message(messages)

                if messages is None: break

                for message_data in messages:
                    message_data = loads(message_data)

                    log(f"{ip_str(*c_address)}: {message_data["text"]}")
                    message_data["timestamps"].append((get_ip(), datetime.now().isoformat()))

                    message_data = encrypt_message(message_data)

                    [cs.sendall(message_data) for cs, _ in self.activeClients]

            except ConnectionResetError: break

        self.activeClients.remove((c_socket, c_address))

        log(f"{ip_str(*c_address)} disconnected!")

        self.stop()


__all__ = ["Server"]

if __name__ == '__main__':
    server = Server()
    server.start(port=12345)
