import unittest
from kavalkilu.net import ServerAPI
from kavalkilu import Hosts, LogWithInflux, Keys


class TestServerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # cls.log = LogWithInflux('server-api')
        cls.api = ServerAPI()

    def setUp(self) -> None:
        pass

    def test_connection(self):
        hosts = self.api._request('/hosts')
        print(hosts)


class TestHosts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.log = LogWithInflux('server-api')
        cls.host = Hosts()

    def setUp(self) -> None:
        pass

    def test_connection(self):
        hosts = self.host.get_all_hosts()
        print(hosts)

    def test_host_and_ip(self):
        haip = self.host.get_host_and_ip(name='pi-garage')
        print(haip)


class TestKeys(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # cls.log = LogWithInflux('server-api')
        cls.key = Keys()

    def setUp(self) -> None:
        pass

    def test_connection(self):
        keys = self.key.get_key('webcam')
        print(keys)

    def test_host_and_ip(self):
        haip = self.host.get_host_and_ip(name='pi-garage')
        print(haip)



if __name__ == '__main__':
    unittest.main()
