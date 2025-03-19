from datetime import datetime
from json import dumps, loads
from typing import Any
from socket import socket


def send_message(socket_: socket, message: str):
    message_data = {
        "message": message,
        "sendTime": datetime.now().isoformat()
    }
    socket_.sendall(f"{dumps(message_data)}\x00".encode("utf-8"))


def decipher_message(message_data: str | bytes) -> list[dict[str, Any]]:
    if isinstance(message_data, bytes): message_data = message_data.decode("utf-8")
    return [loads(m) for m in message_data.split("\x00")[:-1]]


client_address_tuple = tuple[str, int]
cat = client_address_tuple

__all__ = ["send_message", "decipher_message", "cat"]
