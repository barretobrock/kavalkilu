from paho.mqtt.client import Client, MQTTMessage
from typing import Any, Union
from .net import Hosts


class MQTTClient:
    def __init__(self, client_id: str):
        h = Hosts()
        self.client = Client(client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(host=h.get_host('homeserv')['ip'], port=1883, keepalive=60)
        self.connected = True
        self.subscribe = self.client.subscribe
        self.publish = self.client.publish

    @staticmethod
    def _on_connect(client: Client, userdata: Any, flags: Any, rc: int):
        """Set up a callback function to ensure the connection to Server was successful"""
        print(f'Connected with result code {rc}.')

        # Subscribing in on_connect means that if we lose connection and reconnect
        # then subscriptions will be renewed
        client.subscribe('$SYS/#')

    @staticmethod
    def _on_message(client: Client, userdata: Any, msg: MQTTMessage):
        """Callback for when PUBLISH message is received from the server"""
        print(f'{msg.topic} {msg.payload}')

    def disconnect(self):
        """Disconnect from the broker"""
        self.client.disconnect()
        self.connected = False

    def __del__(self):
        """In case class is cleaned up before disconnecting"""
        if self.connected:
            self.disconnect()
