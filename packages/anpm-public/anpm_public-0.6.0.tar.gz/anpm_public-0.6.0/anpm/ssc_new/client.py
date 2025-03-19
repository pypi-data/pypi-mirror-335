from socket import *

from threading import Thread
from datetime import datetime
from json import loads

try: from .shared import *
except ImportError: from shared import *


class Client(socket):
    def __init__(self, log_: bool = True):
        self.connected: bool = False
        self.aliveThread: Thread | None = None
        self.server_address: tuple[str, int] | None = None
        self.log = log_

        super().__init__(AF_INET, SOCK_STREAM)

        if self.log: log("Initiated client...")

    def join(self, ip: str, port: int, *, timeout_: float | None = None):
        self.settimeout(timeout_)

        self.connect((ip, port))

        self.server_address = (ip, port)
        self.connected = True
        self.aliveThread = Thread(target=self.while_alive)
        self.aliveThread.start()

        if self.log: log(f"Connected to {ip_str(ip, port)}!")

    def leave(self):
        self.connected = False

        self.shutdown(SHUT_RDWR)

        if self.log: log(f"Disconnected from {ip_str(*self.server_address)}!")

    def while_alive(self):
        while self.connected:
            messages = self.recv(1024)
            messages = decrypt_message(messages)

            if messages is None: break

            for message_data in messages:
                message_data = loads(message_data)

                message_data["timestamps"].append((get_ip(), datetime.now().isoformat()))

                self.handle_message(message_data)

    def send_message(self, message: str):
        self.send(encrypt_message(message))

    @staticmethod
    def handle_message(message_data: dict):
        log(f"{ip_str(message_data["timestamps"][0][0])}: {message_data["text"]}")


__all__ = ["Client"]

if __name__ == '__main__':
    client = Client()
    client.join("localhost", 12345)

    client.send_message("Hello World!")

    client.leave()
