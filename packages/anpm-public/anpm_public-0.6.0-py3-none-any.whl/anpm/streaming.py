from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable, Literal
from obswebsocket import obsws
from re import search
from requests import get, patch


# noinspection SpellCheckingInspection
class TwitchChat(socket):
    def __init__(self, username: str, token: str, channel: str, client_id: str):
        self.username = username
        self.token = f"oauth:{token}"
        self.channel = channel

        self.client_id = client_id
        self.api_token = token

        super().__init__(AF_INET, SOCK_STREAM)
        self.connect(("irc.chat.twitch.tv", 6667))
        self.send(f"PASS {self.token}\n".encode("utf-8"))
        self.send(f"NICK {self.username}\n".encode("utf-8"))
        self.send(f"JOIN #{self.channel}\n".encode("utf-8"))

    def listen_for_messages(self, called_function: Callable[[str, str], None | Literal["quit"]] = lambda username, message: print(f"{username}: {message.strip()}")):
        while True:
            response = self.recv(2048).decode("utf-8")

            if response.startswith("PING"):
                self.send("PONG :tmi.twitch.tv\n".encode("utf-8"))

            elif "PRIVMSG" in response:
                username = response.split("!")[0][1:]
                message = search(r"PRIVMSG[^:]*:(.*)", response).group(1)

                result = called_function(username, message)
                if result == "quit": break

    def send_message(self, message: str):
        self.send(f"PRIVMSG #{self.channel} :{message}\n".encode("utf-8"))
        print(f"Sent: {message}")

    def update_broadcast_info(self, title: str = None, game_id: str = None):
        url = "https://api.twitch.tv/helix/channels"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Client-Id": self.client_id,
        }
        data = {"broadcaster_id": self.get_broadcaster_id()}

        if title:
            data["title"] = title
        if game_id:
            data["game_id"] = game_id

        response = patch(url, headers=headers, json=data)
        if response.status_code == 204:
            print("Broadcast info updated successfully.")
        else:
            print(f"Failed to update broadcast info: {response.status_code} - {response.text}")

    def get_broadcaster_id(self):
        url = "https://api.twitch.tv/helix/users"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Client-Id": self.client_id,
        }
        params = {"login": self.channel}
        response = get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()["data"][0]["id"]
        else:
            raise Exception(f"Failed to get broadcaster ID: {response.status_code} - {response.text}")


class OBS(obsws):
    def __init__(self, host: str = "localhost", port: int = 4444, password: str = ""):
        super().__init__(host, port, password)
        self.connect()


__all__ = ["TwitchChat", "OBS"]
