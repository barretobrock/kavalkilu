import subprocess


class DomoticzComm:
    """
    Send and receive data from a computer running Domoticz Home Automation server
    Args for __init__:
        server: local IP of server running Domoticz master
        port: Domoticz connection port. default=8080
    """
    def __init__(self, server, port=8080):
        self.server = server
        self.port = port
        self.prefix_url = 'http://{}:{}/json.htm?type=command'.format(self.server, self.port)
        self.curl_type = 'Accept: application/json'

    def switch_on(self, device_id):
        """Sends an 'on' command to a given switch's id"""
        url = '{}&param=switchlight&idx={}&switchcmd=On'.format(self.prefix_url, device_id)
        subprocess.check_call(['curl', '-s', '-i', '-H', self.curl_type, url])

    def switch_off(self, device_id):
        """Sends an 'off' command to a given switch's id"""
        url = '{}&param=switchlight&idx={}&switchcmd=Off'.format(self.prefix_url, device_id)
        subprocess.check_call(['curl', '-s', '-i', '-H', self.curl_type, url])

    def toggle_switch(self, device_id):
        """Toggle a given switch between 'on' and 'off'"""
        url = '{}&param=switchlight&idx={}&switchcmd=Toggle'.format(self.prefix_url, device_id)
        subprocess.check_call(['curl', '-s', '-i', '-H', self.curl_type, url])

    def send_sensor_data(self, device_id, value):
        """
        Send data collected from a certain sensor
        Args:
            device_id: int, id of the given device
            value: float, measurement made by the given sensor
        """
        url = '{}&param=udevice&idx={}&nvalue=0&svalue={}'.format(self.prefix_url, device_id, value)
        subprocess.check_call(['curl', '-s', '-i', '-H', self.curl_type, url])

    def switch_group_off(self, group_id):
        """Switches off a group based on its id"""
        url = '{}&param=switchscene&idx={}&switchcmd=Off'.format(self.prefix_url, group_id)
        subprocess.check_call(['curl', '-s', '-i', '-H', self.curl_type, url])

    def switch_group_on(self, group_id):
        """Switches on a group based on its id"""
        url = '{}&param=switchscene&idx={}&switchcmd=On'.format(self.prefix_url, group_id)
        subprocess.check_call(['curl', '-s', '-i', '-H', self.curl_type, url])
