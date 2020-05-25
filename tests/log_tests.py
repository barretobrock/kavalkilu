import os
from datetime import datetime as dt
import unittest
from ..tools import Log, Paths


class TestLogger(unittest.TestCase):
    def setUp(self) -> None:
        self.log_name = 'test_log'
        self.logg = Log(self.log_name, log_lvl='DEBUG')

    def test_log_path(self):
        self.assertEqual(self.logg.log_path,
                         os.path.join(Paths().log_dir,
                                      *[self.log_name, f"{self.log_name}_{dt.now().strftime('%Y%m%d')}.log"]))

    def test_log_name(self):
        self.assertEqual(self.logg.log_name, f'{self.log_name}_{dt.now():%H%M}')
