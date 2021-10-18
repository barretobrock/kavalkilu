import unittest
from kavalkilu.errors import format_exception


class TestFormatException(unittest.TestCase):
    """Test suite for DateTools class"""
    def test_format_exception(self):
        exc_msg = format_exception(ValueError('This is an exception message.'), incl_traceback=False)
        exc_msg = format_exception(ValueError('This is an exception message.'), incl_traceback=True)
