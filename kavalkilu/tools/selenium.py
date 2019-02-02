#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Handles exceptions while interacting with Selenium objects
"""
import time
import datetime
from random import randint
from selenium.webdriver import Chrome
from selenium.webdriver import PhantomJS
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class ChromeDriver(Chrome):
    """
    Initiates Chromedriver for Selenium
    Args for __init__:
        driver_path: path to Chromedriver
        timeout: int, seconds to wait until connection unsuccessful
        options: list, any extra options to add to chrome_options.add_argument()
    """
    default_options = [
        '--disable-extensions',
        '--mute-audio',
        '--disable-infobars',   # Get rid of "Chrome is being controlled by automated software" notification
        '--start-maximized'
    ]

    def __init__(self, driver_path='/usr/bin/chromedriver', timeout=60, options=default_options):
        self.driver_path = driver_path
        # Add options to Chrome
        chrome_options = Options()
        if options is not None:
            for option in options:
                chrome_options.add_argument(option)
        # Disable notifications
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
        }
        chrome_options.add_experimental_option('prefs', prefs)
        # Apply options
        super(ChromeDriver, self).__init__(self.driver_path, chrome_options=chrome_options)
        # Set timeout for 1 minute to avoid multiple instances opening over time
        super(ChromeDriver, self).set_page_load_timeout(timeout)


class PhantomDriver(PhantomJS):
    """
    Initiates the PhantomJS driver for Selenium
    Args for __init__:
        driver_path: path to Chromedriver
        timeout: int, seconds to wait until connection unsuccessful
    """
    default_service_args = [
        # For PhantomJS, SSL should be disabled as it is not compliant with the most recent version
        '--ignore-ssl-errors=true',
        '--ssl-protocol=any'
    ]

    def __init__(self, driver_path='/usr/bin/chromedriver', timeout=60, service_args=default_service_args):
        self.driver_path = driver_path
        # Apply options
        super(PhantomDriver, self).__init__(self.driver_path, service_args=service_args)
        # Set timeout for 1 minute to avoid multiple instances opening over time
        super(PhantomDriver, self).set_page_load_timeout(timeout)


class Action:
    """
    Performs action to Selenium-class webdriver
    Args for __init__:
        driver: Selenium-type driver class
    """
    # Predefined wait ranges, in seconds
    slow_wait = [15, 30]
    medium_wait = [5, 15]
    fast_wait = [0.5, 5]

    def __init__(self, driver):
        self.driver = driver

    def get(self, url):
        """
        Navigates browser to url
        Args:
            url: str, url to navigate to
        """
        self.driver.get(url)

    def click(self, xpath):
        """
        Clicks HTML element
        Args:
            xpath: str, xpath to element to click
        """
        d = self.driver.find_element_by_xpath
        for i in range(0, 3):
            try:
                d(xpath).click()
                break
            except:
                self.announce_exception(i + 1)

    def clear(self, xpath):
        """
        Clears form element of text
        Args:
            xpath: str, xpath to form element
        """
        d = self.driver.find_element_by_xpath
        for i in range(0, 3):
            try:
                d(xpath).clear()
                break
            except:
                self.announce_exception(i + 1)

    def enter(self, xpath, entry_text):
        """
        Enters text into form element
        Args:
            xpath: str, xpath to form
            entry_text: str, text to enter into form
        """
        d = self.driver.find_element_by_xpath
        for i in range(0, 3):
            try:
                d(xpath).send_keys(entry_text)
                break
            except:
                self.announce_exception(i + 1)

    def elem_exists(self, xpath):
        """
        Determines if particular element exists
        Args:
            xpath: str, xpath to HTML element
        Returns: True if exists
        """
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except:
            return False

    def get_elem(self, xpath, single=True):
        """
        Returns HTML elements as selenium objects
        Args:
            xpath: str, xpath of element to return
            single: boolean, True if returning only one element. default: True
        Returns: HTML element(s) matching xpath text
        """
        if single:
            d = self.driver.find_element_by_xpath
        else:
            d = self.driver.find_elements_by_xpath
        for i in range(0, 3):
            try:
                return d(xpath)
            except:
                self.announce_exception(i + 1)
        return None

    def get_text(self, xpath, single=True):
        """
        Returns text in element(s)
        Args:
            xpath: str, xpath to element
            single: boolean, Whether to extract from single element or multiple. default = True
        Returns: Text from inside element(s)
        """
        if single:
            d = self.driver.find_element_by_xpath
            for i in range(0, 3):
                try:
                    elem = d(xpath)
                    return elem.text
                except:
                    self.announce_exception(i + 1)
        else:
            d = self.driver.find_elements_by_xpath
            for i in range(0, 3):
                try:
                    elems = d(xpath)
                    text_list = []
                    for e in elems:
                        text_list.append(e.text)
                    return text_list
                except:
                    self.announce_exception(i + 1)
        return ""

    def remove(self, xpath, single=True):
        """
        Uses JavaScript commands to remove desired element
        Args:
            xpath: str, xpath to element
            single: boolean whether to apply to single element or multiple. default = True
        """
        script = """
        var element = arguments[0];
        element.remove();
        """
        if single:
            d = self.driver.find_element_by_xpath
            for i in range(0, 3):
                try:
                    elem = d(xpath)
                    self.driver.execute_script(script, elem)
                    break
                except:
                    self.announce_exception(i + 1)
        else:
            d = self.driver.find_elements_by_xpath
            for i in range(0, 3):
                try:
                    elems = d(xpath)
                    for e in elems:
                        self.driver.execute_script(script, e)
                    break
                except:
                    self.announce_exception(i + 1)

    def rand_wait(self, sleep_range_secs):
        """
        Determines sleep time as random number between upper and lower limit,
            then sleeps for that given time. After sleep, moves randomly vertically and horizontally on page
            for up to four times
        Args:
            sleep_range_secs: list, min and max number of seconds to sleep
        """

        if len(sleep_range_secs) == 2:
            sleep_secs_lower, sleep_secs_higher = tuple(sleep_range_secs)
        else:
            raise ValueError('Input for sleep range must be exactly two items')
        sleeptime = randint(sleep_secs_lower, sleep_secs_higher)
        time.sleep(sleeptime)
        # after wait period, scroll through window randomly
        for i in range(4):
            r_x = randint(-20, 20)
            r_y = randint(150, 300)
            s = "window.scrollBy({},{})".format(r_x, r_y)
            self.driver.execute_script(s)

    def scroll_to_element(self, elem, use_selenium_method=True):
        """
        Scrolls to get element in view
        Args:
            elem: Selenium-class element
            use_selenium_method: bool, if True, uses built-in Selenium method of scrolling an element to view
                otherwise, uses Javascript (scrollIntoView)
        """
        if use_selenium_method:
            actions = ActionChains(self.driver)
            actions.move_to_element(elem).perform()
        else:
            self.driver.execute_script('arguments[0].scrollIntoView();', elem)

    def announce_exception(self, num_attempt):
        """
        Prints when exception encountered
        Args:
            num_attempt: int, number of previous attempts in current task
        """
        print("Exceptions encountered: {}".format(num_attempt))
        time.sleep(2)

