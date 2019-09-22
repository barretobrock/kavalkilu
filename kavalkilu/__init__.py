#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kavalkilu: A Library for Integrating Home Automation Components
"""
__update_date__ = '2019-08-21'

# camera.py
from .tools import Amcrest, SecCamGroup, AmcrestWeb, Camera
# databases.py
from .tools import MySQLLocal, PiHoleDB, CSVHelper
# date.py
from .tools import DateTools
# domoticz.py
from .tools import Domoticz
# gif.py
from .tools import GIF, GIFSlice, GIFTile
# gpio.py
from .tools import GPIO
# image.py
from .tools import IMG, IMGSlice
# light.py
from .tools import HueBulb, LED, hue_lights
# log.py
from .tools import Log
# message.py
from .tools import PBullet, Email
# net.py
from .tools import Hosts, HostsRetrievalException, Keys, KeyRetrievalException, NetTools
# openhab.py
from .tools import OpenHab
# path.py
from .tools import Paths
# relay.py
from .tools import Relay
# secure_copy.py
# from .tools import
# selenium.py
from .tools import ChromeDriver, PhantomDriver, BrowserAction
# sensors.py
from .tools import DHTTempSensor, DallasTempSensor, DistanceSensor, PIRSensor, SensorLogger, DarkSkyWeatherSensor
# serial.py
# from .tools import
# slack.py
from .tools import SlackBot, SlackTools
# system.py
from .tools import SysTools
# text.py
from .tools import MarkovText, WebExtractor, TextHelper, TextCleaner
# weather.py
from .tools import DarkSkyWeather

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
