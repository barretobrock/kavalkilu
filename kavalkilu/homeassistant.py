from typing import (
    Dict,
    List,
)

from loguru import logger
import requests

from kavalkilu.net import (
    Hosts,
    Keys,
)


class HAHelper:
    """Wrapper for Home Assistant methods

    Docs: https://developers.home-assistant.io/docs/api/rest/
    """
    PORT = 8123

    def __init__(self):
        self.ip = Hosts().get_ip_from_host('homeassistant')
        self.base_url = f'http://{self.ip}:{self.PORT}/api'
        self.auth = Keys().get_key('home-assistant').get('token', '')
        self.headers = {
            'Authorization': f'Bearer {self.auth}',
            'content-type': 'application/json'
        }

    def _get(self, path: str) -> requests.Response:
        """Handles requests for the class"""
        url = f'{self.base_url}{path}'
        logger.debug(f'Sending GET to path {path}')
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp

    def _post(self, path: str, payload: Dict = None) -> requests.Response:
        """Handles requests for the class"""
        url = f'{self.base_url}{path}'
        logger.debug(f'Sending POST to path {path}')

        if 'webhook' in path:
            resp = requests.post(url)
        else:
            resp = requests.post(url, headers=self.headers, json=payload)

        resp.raise_for_status()
        return resp

    def call_webhook(self, hook_name: str):
        """Sends a call to an automation with a webhook trigger"""
        _ = self._post(f'/webhook/{hook_name}')

    def get_state(self, device_name: str) -> Dict:
        resp = self._get(f'/states/{device_name}')
        return resp.json()

    def get_states(self) -> List[Dict]:
        resp = self._get('/states')
        return resp.json()

    def set_state(self, device_name: str, data: dict, data_class: str = None, attributes: Dict = None):
        if attributes is None:
            attributes = {}
        if data_class is not None:
            if data_class in ['temp', 'temperature']:
                attributes.update({'unit_of_measurement': '°C', 'device_class': 'temperature'})
            elif data_class in ['hum', 'humidity']:
                attributes.update({'unit_of_measurement': '%', 'device_class': 'humidity'})
        if len(attributes) > 0:
            data.update({'attributes': attributes})
        _ = self._post(f'/states/{device_name}', data)
