"""Net-related tools"""
import requests
import subprocess
import re
import socket
from typing import List, Union


class HostsRetrievalException(Exception):
    pass


class KeyRetrievalException(Exception):
    pass


class Server:
    def __init__(self):
        self.server_ip = '192.168.1.5'
        self.port = 5002

    def server_addr(self) -> str:
        """Displays server address"""
        return f'http://{self.server_ip}:{self.port}'


class Hosts:
    """Captures host info from API call"""
    def __init__(self):
        s_api = Server()
        self.api_url = f'{s_api.server_addr()}/hosts'
        response = requests.get(self.api_url)
        if response.status_code == 200:
            hostdata = response.json()
            if 'data' in hostdata.keys():
                self.hosts = hostdata['data']
        else:
            raise HostsRetrievalException(f'Error requesting data. ErrCode: {response.status_code}')

    def get_host(self, name: str = None, ip: str = None) -> dict:
        """Returns host at name or ip.
        Name or IP must be used.

        Args:
            name: str, if used, will return the host at the given name
            ip: str, if used, will return the host at the given ip

        Returns: dict, with keys 'name' and 'ip'
        """

        if not any([name is not None, ip is not None]):
            # Throw exception if nothing is set
            raise HostsRetrievalException('You must use name or ip in the args of get_host')

        for item in self.hosts:
            if name is not None:
                if item['name'] == name:
                    return item
            elif ip is not None:
                if item['ip'] == ip:
                    return item

    def get_hosts(self, regex: str, key: str = 'name') -> List[dict]:
        """Returns host at name or ip.
        Name or IP must be used.

        Args:
            regex: str, regex string to use to search
            key: str, which key to search in the dict

        Returns: list of dict, with keys 'name' and 'ip'
        """
        # Build the regex filter
        rex = re.compile(regex)

        matches = []
        for item in self.hosts:
            if rex.match(item[key]):
                matches.append(item)

        return matches


class Keys:
    """Captures credential info from API call
    These will eventually be put into a database complete with token-based
        authentication to avoid having these credentials accessible to all
        users on my WiFi. For now, this will be the case.
    """
    def __init__(self):
        s_api = Server()
        self.api_url = f'{s_api.server_addr()}/keys'
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data.keys():
                self.keys = data['data']
        else:
            raise KeyRetrievalException(f'Error requesting data. ErrCode: {response.status_code}')

    def get_key(self, name: str) -> Union[str, dict]:
        """Returns key by name"""

        if name is None:
            # Throw exception if nothing is set
            raise KeyRetrievalException('You must enter a valid key name.')

        for item in self.keys:
            if item['name'] == name:
                keys = item['keys']
                if isinstance(keys, str):
                    # Remove extra whitespace if returning only string
                    return keys.strip()
                else:
                    return item['keys']
        # If we arrived here, the key wasn't found
        raise KeyRetrievalException(f'The key ({name}) was not found in the database.')


class NetTools:
    """For pinging an ip address"""

    def __init__(self, host: str = None, ip: str = None):
        if host is not None:
            # First, look up the hostname
            self.ip = Hosts().get_host(name=host)['ip']
        elif ip is not None:
            self.ip = ip
        else:
            self.ip = self.get_ip()

    def ping(self, n_times: int = 2) -> bool:
        """Pings an IP up to n times"""
        ping_cmd = ['ping', '-c', '1', self.ip]

        for t in range(n_times):
            proc = subprocess.Popen(ping_cmd, stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if proc.returncode == 0:
                # Successfully pinged
                return True
        # Unsuccessfully pinged
        return False

    @staticmethod
    def get_ip() -> str:
        # Elaborate machine name from ip
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        ip_addr = sock.getsockname()[0]
        sock.close()
        return ip_addr
