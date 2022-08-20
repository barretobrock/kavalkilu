import unittest
from unittest.mock import (
    MagicMock,
    patch,
)

from kavalkilu import (
    Hosts,
    Keys,
)
from kavalkilu.net import ServerAPI
from tests.mocks import MockResponse


class TestServerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = ServerAPI()

    def setUp(self) -> None:
        pass

    def test_connection(self):
        hosts = self.api._request('/api/hosts')
        print(hosts)


class TestHosts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.host = Hosts()

    def setUp(self) -> None:
        pass

    def test_connection(self):
        hosts = self.host.get_all_hosts()
        print(hosts)

    @patch('requests.get')
    def test_host_and_ip(self, mock_get: MagicMock):

        mock_get.return_value = MockResponse({'data': [
            {
                'ip': '192.168.99.99',
                'machine_type': 'unknown',
                'name': 'something'
            }
        ]}, 200)
        haip = self.host.get_host_and_ip(name='pi-garage')
        print(haip)


class TestKeys(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.key = Keys()

    def setUp(self) -> None:
        pass

    def test_connection(self):
        keys = self.key.get_key('webcam')
        print(keys)


if __name__ == '__main__':
    unittest.main()
