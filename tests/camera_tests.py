#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from kavalkilu import Hosts, Keys
from ..tools.camera import Amcrest, SecCamGroup


class TestAmcrest:
    creds = Keys().get_key('webcam_api')
    known_ip = Hosts().get_host(name='ac-elutuba')['ip']
    unknown_ip = '192.168.3.234'

    def test_known_init(self):
        cam = Amcrest(self.known_ip, self.creds)
        assert cam is not None

    def test_unknown_init(self):
        cam = Amcrest(self.unknown_ip, self.creds)
        assert cam is not None



