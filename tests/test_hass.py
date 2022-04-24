import unittest
from kavalkilu import HAHelper


class TestHASS(unittest.TestCase):
    """Test HA Helper methods"""
    @classmethod
    def setUpClass(cls) -> None:
        cls.hass = HAHelper()

    def setUp(self) -> None:
        pass

    def test_webhook(self):
        self.hass.call_webhook('doorbell_pressed')

    def test_state_call(self):
        """Test GET state"""
        sensor = 'binary_sensor.garage_door'
        self.hass.set_state(sensor, {'state': 'closed'})
        state = self.hass.get_state(sensor)
        self.assertTrue(state.get('state') == 'closed')
        self.hass.set_state(sensor, {'state': 'open'})
        state = self.hass.get_state(sensor)
        self.assertTrue(state.get('state') == 'open')
        self.hass.set_state(sensor, {'state': 'closed'})


if __name__ == '__main__':
    unittest.main()
