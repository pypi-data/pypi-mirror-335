from socket import *

from .Shared import *


class Client(socket):
    def __init__(self):
        super().__init__()
        self.connected: bool = False

    def join(self, ip, port):
        super().__init__(AF_INET, SOCK_STREAM)
        self.connect((ip, port))

        self.connected = True

    def leave(self):
        self.connected = False
        self.shutdown(SHUT_RDWR)
        self.close()


__all__ = ["Client"]

if __name__ == '__main__':
    client = Client()
    client.join("localhost", 1234)

    send_message(client, "Hello World!")

    client.leave()
