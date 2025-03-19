from colorama import Fore
from datetime import datetime
from socket import gethostbyname, gethostname
from json import dumps


def log(message: str):
    print(f"{Fore.LIGHTBLUE_EX}[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}]: {Fore.RESET}{message}")


def ip_str(ip: str, port: int | None = None) -> str: return f"{Fore.GREEN}{ip}{f":{port}" if port is not None else ""}{Fore.RESET}"


def get_ip() -> str: return gethostbyname(gethostname())


def decrypt_message(message: bytes) -> list[str] | None:
    if message == b'': return None

    message = message.decode("utf-8")
    messages = message.split("\x00")[:-1]

    return messages


def encrypt_message(message_data: dict | str) -> bytes:
    if isinstance(message_data, str):
        message_data = {
            "text": message_data,
            "timestamps": [(get_ip(), datetime.now().isoformat())],
            "type": "message"
        }

    return f"{dumps(message_data)}\x00".encode("utf-8")


__all__ = ["log", "ip_str", "get_ip", "decrypt_message", "encrypt_message"]
