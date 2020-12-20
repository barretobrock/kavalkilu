"""Net-related tools"""
import requests
import subprocess
import re
import socket
import uuid
from typing import List, Dict


class HostsRetrievalException(Exception):
    pass


class KeyRetrievalException(Exception):
    pass


class ServerAPI:
    """Basic methods for communicating with the main server api """
    def __init__(self):
        self.server = 'tinyserv'
        self.port = 5002
        self.url = f'http://{self.server}.local:{self.port}'

    def _request(self, path: str, params: Dict[str, str] = None) -> List[Dict[str, str]]:
        response = requests.get(f'{self.url}{path}', params=params)
        if response.status_code == 200:
            return response.json().get('data')
        else:
            response.raise_for_status()


class Hosts(ServerAPI):
    """Captures host info from API call"""
    def __init__(self):
        super().__init__()

    def get_all_hosts(self) -> List[Dict[str, str]]:
        return self._request('/hosts')

    def get_host_and_ip(self, name: str = None, ip: str = None) -> Dict[str, str]:
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
        # This should only yield one result
        result = self._request('/host', params={'name': name, 'ip': ip})
        if len(result) > 0:
            return result[0]
        return {}

    def get_host_from_ip(self, ip: str) -> str:
        """Returns hostname from ip"""
        return self.get_host_and_ip(ip=ip).get('name', None)

    def get_ip_from_host(self, host: str) -> str:
        """Returns hostname from ip"""
        return self.get_host_and_ip(name=host).get('ip', None)

    def get_hosts_and_ips(self, regex: str, key: str = 'name') -> List[dict]:
        """Returns host at name or ip.
        Name or IP must be used.

        Args:
            regex: str, regex string to use to search
            key: str, which key to search in the dict

        Returns: list of dict, with keys 'name' and 'ip'
        """
        # Build the regex filter
        rex = re.compile(regex)
        hosts = self.get_all_hosts()
        matches = []
        for item in hosts:
            if rex.match(item[key]):
                matches.append(item)

        return matches


class Keys(ServerAPI):
    """Captures credential info from API call
    These will eventually be put into a database complete with token-based
        authentication to avoid having these credentials accessible to all
        users on my WiFi. For now, this will be the case.
    """
    def __init__(self):
        super().__init__()

    def get_key(self, name: str) -> Dict[str, str]:
        """Returns key by name"""

        if name is None:
            # Throw exception if nothing is set
            raise KeyRetrievalException('You must enter a valid key name.')

        result = self._request(f'/key/{name}')
        if len(result) > 0:
            return result[0]
        return {}


class NetTools:
    """For pinging an ip address"""

    def __init__(self):
        self.ip = self.get_ip()
        self.hostname = self.get_hostname()

    @staticmethod
    def ping_ip(ip: str, n_times: int = 2) -> bool:
        """Pings an IP up to n times"""
        ping_cmd = ['ping', '-c', '1', ip]

        for t in range(n_times):
            proc = subprocess.Popen(ping_cmd, stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if proc.returncode == 0:
                # Successfully pinged
                return True
        # Unsuccessfully pinged
        return False

    @staticmethod
    def get_hostname() -> str:
        """Gets machine's hostname"""
        return socket.gethostname()

    @staticmethod
    def get_ip() -> str:
        """Gets machine's IP"""
        # Elaborate machine name from ip
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        ip_addr = sock.getsockname()[0]
        sock.close()
        return ip_addr

    @staticmethod
    def get_mac() -> str:
        """Gets mac address of machine"""
        return ':'.join(list(map(str.upper, re.findall(r'..', f'{uuid.getnode():012x}'))))
