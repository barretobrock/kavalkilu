#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
import json
from datetime import datetime as dtt
from kavalkilu import Log, Paths
from kavalkilu.tools.selenium import ChromeDriver, Action


logg = Log('vpulse_auto', log_lvl='DEBUG')
p = Paths()

# TODO
# build out a table of when monthly, weekly things were last done.
# Reformat chromedriver so I can add in options as arguments (e.g., mute)
# Handle weekly tasks either based on DOW or recorded table with date_last_done and freq columns
# Also figure out how to do cards, daily habits

# Get credentials
with open(os.path.join(p.key_dir, 'vpulse_creds.txt')) as f:
    creds = json.loads(f.read())

today = dtt.today()
c = ChromeDriver('/usr/bin/chromedriver')
a = Action(c)
logg.debug('Chrome instantiated.')

vpulse_home_url = 'https://member.virginpulse.com/'
c.get(vpulse_home_url)
a.rand_wait('medium')

a.enter('//input[@id="username"]', creds['user'])
a.enter('//input[@id="password"]', creds['password'])
a.click('//input[@id="kc-login"]')

# Try to find the popup close button
try:
    pu_close_btn = c.find_element_by_xpath('//div[@id="rophy-modal-close-btn"]')
except:
    pu_close_btn = None
if pu_close_btn is not None:
    pu_close_btn.click()
a.rand_wait('medium')

# Do the financial wellness thing
fw_url = 'https://www.moneyhabits.co/virginpulse'
c.get(fw_url)
a.rand_wait('medium')
budget_url = 'https://www.moneyhabits.co/web-fe/budgeting'
c.get(budget_url)
a.rand_wait('medium')

if today.strftime('%d') == 1:
    # First of month, adjust budget
    c.get(budget_url)
    a.click('//div/button[contains(text(), "Set Budget"]')

# Do the Fitness tracker thing
fitness_url = 'https://www.myfitnesspal.com/account/login'
c.get(fitness_url)
a.rand_wait('medium')
a.enter('//input[@id="username"]', creds['user'])
a.enter('//input[@id="password"]', creds['password'])
a.click('//input[@type="submit"]')
a.rand_wait('medium')

food_diary_url = 'https://www.myfitnesspal.com/food/diary'
c.get(food_diary_url)

# Quick add calories
quick_add_url = 'https://www.myfitnesspal.com/food/copy_meal?date={:%F}&from_date=2019-01-24&from_meal=0&username=obrock2'.format(today)
c.get(quick_add_url)
a.rand_wait('medium')


# Do the recipes thing
recipe_url = 'https://member.virginpulse.com/devices/zipongosso'
c.get(recipe_url)
# If popup, disable
try:
    pu_get_app = c.find_element_by_xpath('//div[@id="interstitial-content-close"]/span')
except:
    pu_get_app = None

if pu_get_app is not None:
    pu_get_app.click()

# Meal buttons to click
meal_btns = c.find_elements_by_xpath('//button[@class="button-green dash-meal-button"]')
meal_btns[1].click()

if today.strftime('%u') == 1:
    logg.info('Performing weekly activities')
    # If a monday, favorite a recipe and add to grocery list
    # Favorite (once weekly)
    logg.info('Favoriting recipe')
    a.click('//div[@class="heart"]')

    logg.info('Adding recipe to grocery list')
    # Add to grocery list (once weekly)
    a.click('//div[@class="action-text"]/span[text()="Add to Grocery List"]')
    # Confirm add
    a.click('//div[@class="grocery-list-add-modal-confirm-container"]')


# Healthy habits
hh_url = "https://app.member.virginpulse.com/#/healthyhabits"
c.get(hh_url)
yes_btns = c.find_elements_by_xpath('//div/button[contains(@class, "btn-choice-yes")]')

clicks = 0
for yes_btn in yes_btns:
    if clicks > 3:
        break
    if 'green-button' not in yes_btn.get_attribute('class'):
        # Button not clicked
        # Scroll to button
        c.execute_script("arguments[0].scrollIntoView();", yes_btn)
        c.execute_script("document.getElementById('{}').click()".format(yes_btn.get_attribute('id')))
        clicks += 1
    a.rand_wait('fast')


# Complete a WHIL session
whil_url = "https://connect.whil.com/virginpulsesso/redirect?destination=home"
c.get(whil_url)

# Play a specific session
body_sense_url = "https://connect.whil.com/goaltags/freemium-mindfulness-101/sessions/sense-the-body"
c.get(body_sense_url)
a.click('//div/img[@alt="play"]')
# Wait five mins
time.sleep(300)

c.quit()
