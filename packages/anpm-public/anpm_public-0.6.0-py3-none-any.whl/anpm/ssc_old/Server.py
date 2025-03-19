from socket import *
from threading import Thread
from datetime import datetime
from typing import Any, Callable

from .Shared import *


class Server(socket):
    def __init__(self):
        super().__init__()

        self.running: bool = False
        self.activeClients: list[tuple[socket, cat]] = []

        self.fClientConnect: Callable[[socket, cat], None] = lambda cs, ca: print(f"New connection from {ca[0]}.")
        self.fClientDisconnect: Callable[[socket, cat], None] = lambda cs, ca: print(f"{ca[0]} disconnected.")
        self.fRecieveData: Callable[[socket, cat, dict[str, Any]], None] = lambda cs, ca, mdata: print(mdata)
        self.fServerClose: Callable[[], None] = lambda: print("Server closed.")
        self.fServerStart: Callable[[str, int], None] = lambda ip, port: print(f"Now listening on {ip}:{port}.")

    def start(self, ip: str, port: int, backlog: int = 1):
        super().__init__(AF_INET, SOCK_STREAM)
        self.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.bind((ip, port))
        self.listen(backlog)
        self.running = True

        def accept_clients():
            while self.running:
                try:
                    Thread(target=self.handle_client, args=(*self.accept(),)).start()
                except OSError as e:
                    if e.errno != 10038: raise e
                    break

        Thread(target=accept_clients, daemon=True).start()

        self.fServerStart(ip, port)

    def wait(self):
        while self.running: ...

    def stop(self):
        self.running = False
        self.fServerClose()
        self.close()

    def handle_client(self, client_socket: socket, client_address: tuple[str, int]):
        csa = (client_socket, client_address)
        self.activeClients.append(csa)

        self.fClientConnect(*csa)

        while self.running:
            message_data = client_socket.recv(1024)
            if not message_data: break

            for mdata in decipher_message(message_data):
                mdata["recieveTime"] = datetime.now().isoformat()

                self.fRecieveData(*csa, mdata)

            self.stop()

        self.activeClients.remove(csa)

        self.fClientDisconnect(*csa)


__all__ = ["Server"]

if __name__ == '__main__':
    server = Server()
    server.start("localhost", 1234)
    server.wait()
