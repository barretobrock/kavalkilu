#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyecobee
from pyecobee import SelectionType, Selection


dev = pyecobee.EcobeeService('Home', "TZ6wpsxYGl18hOgG6eQB8ocepiMq97FS")
dev.refresh_tokens()
auth = dev.authorize(timeout=30)

select = Selection(selection_type=SelectionType.REGISTERED.value)

therm = dev.request_thermostats(select)