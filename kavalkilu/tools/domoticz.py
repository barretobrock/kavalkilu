import subprocess
from typing import Union


class Domoticz:
    """
    Send and receive data from a computer running Domoticz Home Automation server
    Args for __init__:
        server: local IP of server running Domoticz master
        port: Domoticz connection port. default=8080
    """
    def __init__(self, server: str, port: int = 8080):
        self.server = server
        self.port = port
        self.prefix_url = f'http://{self.server}:{self.port}/json.htm?type=command'
        self.curl_type = 'Accept: application/json'

    def _send_command(self, cmd_url: str):
        """Send the command to the server via cURL"""
        subprocess.check_call(['curl', '-s', '-i', '-H', self.curl_type, cmd_url])

    def switch_on(self, device_id: Union[int, str]):
        """Sends an 'on' command to a given switch's id"""
        url = f'{self.prefix_url}&param=switchlight&idx={device_id}&switchcmd=On'
        self._send_command(url)

    def switch_off(self, device_id: Union[int, str]):
        """Sends an 'off' command to a given switch's id"""
        url = f'{self.prefix_url}&param=switchlight&idx={device_id}&switchcmd=Off'
        self._send_command(url)

    def toggle_switch(self, device_id: Union[int, str]):
        """Toggle a given switch between 'on' and 'off'"""
        url = f'{self.prefix_url}&param=switchlight&idx={device_id}&switchcmd=Toggle'
        self._send_command(url)

    def send_sensor_data(self, device_id: Union[int, str], value: float):
        """
        Send data collected from a certain sensor
        Args:
            device_id: int, id of the given device
            value: float, measurement made by the given sensor
        """
        url = f'{self.prefix_url}&param=udevice&idx={device_id}&nvalue=0&svalue={value}'
        self._send_command(url)

    def switch_group_off(self, group_id):
        """Switches off a group based on its id"""
        url = f'{self.prefix_url}&param=switchscene&idx={group_id}&switchcmd=Off'
        self._send_command(url)

    def switch_group_on(self, group_id):
        """Switches on a group based on its id"""
        url = f'{self.prefix_url}&param=switchscene&idx={group_id}&switchcmd=On'
        self._send_command(url)
