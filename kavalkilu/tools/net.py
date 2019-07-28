"""Net-related tools"""
import requests
import re


class HostsRetrievalException(Exception):
    pass


class Hosts:
    """Captures host info from API call"""
    def __init__(self):
        self.server = '192.168.0.5'
        self.port = 5002
        self.api_url = 'http://{}:{}/hosts'.format(self.server, self.port)
        response = requests.get(self.api_url)
        if response.status_code == 200:
            hostdata = response.json()
            if 'data' in hostdata.keys():
                self.hosts = hostdata['data']
        else:
            raise HostsRetrievalException('Error requesting data. ErrCode: {}'.format(response.status_code))

    def get_host(self, name=None, ip=None):
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

    def get_hosts(self, regex, key='name'):
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
