from datetime import datetime as dt
import unittest
from kavalkilu import Log, Path


class TestLogger(unittest.TestCase):
    def setUp(self) -> None:
        self.log_name = 'test_log'
        self.logg = Log(self.log_name, log_lvl='DEBUG')
        self.child_logg = Log(self.log_name, child_name='child')

    def test_log_path(self):
        kpath = Path()
        self.assertEqual(
            self.logg.log_path,
            kpath.easy_joiner(
                kpath.logs_dir,
                [self.log_name, f"{self.log_name}_{dt.now().strftime('%Y%m%d')}.log"]
            )
        )

    def test_log_name(self):
        self.assertEqual(self.logg.log_name, f'{self.log_name}_{dt.now():%H%M}')

    def test_child_log(self):
        self.logg.debug('Hello')
        self.child_logg.debug('Hello')


