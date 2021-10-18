from typing import (
    Dict
)


class MockResponse:
    def __init__(self, json_data: Dict, status_code: float):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
