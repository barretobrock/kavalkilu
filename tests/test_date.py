from datetime import datetime as dt
import unittest

from dateutil import tz
from dateutil.relativedelta import relativedelta

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
        unix = self.dtools.dt_to_unix(only_dt, from_tz=self.dtools.TZ_CT)
        dt_w_tz = dt.now(tz=tz.gettz('UTC'))
        unix_tz = self.dtools.dt_to_unix(dt_w_tz, from_tz=self.dtools.TZ_UTC)
        self.assertTrue(unix_tz == unix)
        # Convert back
        unix_tz_back_to_dt = self.dtools.unix_to_dt(unix_tz, to_tz='US/Central')
        unix_back_to_dt = self.dtools.unix_to_dt(unix)
        self.assertEqual(unix_tz_back_to_dt.time(), unix_back_to_dt.time())

    def test_last_day_of_month(self):
        nov = dt(2021, 11, 30)
        result = self.dtools.last_day_of_month(nov)
        self.assertEqual(nov.day, result.day)

    def test_str_to_datetime(self):
        nov = dt(2021, 11, 30, 4, 45, 34)
        result = self.dtools.string_to_datetime(nov.strftime(self.dtools.ISO_DATETIME_STR))
        self.assertEqual(nov, result)
        result = self.dtools.string_to_datetime(nov.strftime(self.dtools.ISO_DATETIME_STR),
                                                strftime_string=self.dtools.ISO_DATETIME_STR)
        self.assertEqual(nov, result)

    def test_str_to_unx(self):
        dt_str = dt.now().strftime(self.dtools.ISO_DATETIME_STR)
        unix = self.dtools.string_to_unix(dt_str)
        self.assertEqual(dt_str, self.dtools.unix_to_string(unix))

    def test_human_readable_date(self):
        # Get a date 1y, 2 months, 3 days 5 hours, 30 mins apart
        now = dt.now()
        then = (now + relativedelta(years=1, months=2, days=3, hours=5, minutes=30))
        self.assertEqual('1y 2mo 3d 5h 30m', self.dtools.get_human_readable_date_diff(now, then))

    def test_tz_convert(self):
        ct = dt.now()
        utc = dt.utcnow()
        self.assertEqual(utc.hour, self.dtools._tz_convert('US/Central', 'UTC', ct).hour)


if __name__ == '__main__':
    unittest.main()
