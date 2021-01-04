import unittest
from datetime import datetime as dt
from dateutil import tz
from kavalkilu import DateTools


class TestDateTools(unittest.TestCase):
    """Test suite for DateTools class"""
    @classmethod
    def setUpClass(cls) -> None:
        cls.dtools = DateTools()

    def setUp(self) -> None:
        pass

    def test_dt_to_unix(self):
        """Test converting datetime to unix with and without timezone"""
        only_dt = dt.now()
        unix = self.dtools.dt_to_unix(only_dt, from_tz='US/Central')
        dt_w_tz = dt.now(tz=tz.gettz('UTC'))
        unix_tz = self.dtools.dt_to_unix(dt_w_tz)
        self.assertTrue(unix_tz == unix)
        # Convert back
        unix_tz_back_to_dt = self.dtools.unix_to_dt(unix_tz, to_tz='US/Central')
        unix_back_to_dt = self.dtools.unix_to_dt(unix)
        self.assertTrue(unix_tz_back_to_dt.time() == unix_back_to_dt.time())


if __name__ == '__main__':
    unittest.main()
