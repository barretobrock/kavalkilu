#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
import json
from datetime import datetime as dtt
from collections import OrderedDict
from kavalkilu import Log, Paths
from kavalkilu.tools.selenium import ChromeDriver, Action


logg = Log('vpulse_auto', log_lvl='DEBUG')
p = Paths()

# TODO
# build out a table of when monthly, weekly things were last done.
# Handle weekly tasks either based on DOW or recorded table with date_last_done and freq columns

# Get credentials
with open(os.path.join(p.key_dir, 'vpulse_creds.txt')) as f:
    creds = json.loads(f.read())

today = dtt.today()
c = ChromeDriver('/usr/bin/chromedriver')
a = Action(c)
logg.debug('Chrome instantiated.')


def popup_closer():
    # Try to find the popup close button
    try:
        # This gets tricky, because the box takes several seconds to pop up sometimes
        #a.rand_wait(a.slow_wait)
        # Scroll back up to the top
        c.execute_script('window.scrollTo(0, 0);')
        pu_close_btn = c.find_element_by_xpath('//div[@id="trophy-modal-close-btn"]')
        pu_close_btn.click()
        logg.debug('Popup close button likely successfully clicked.')
    except:
        logg.debug('Popup close button non-existent, or unable to be clicked.')
        a.rand_wait(a.medium_wait)


def daily_cards():
    """Handles the daily cards section"""
    c.execute_script('window.scrollTo(0, 0);')
    card_btn = a.get_elem('//div[@class="home-cards-wrapper"]/div[div/div[@translate="Core.CoreHome.Cards"]]')
    # Get the class of the child div
    child_div = card_btn.find_element_by_xpath('.//div')
    if 'active-view' not in child_div.get_attribute('class'):
        # Card view not already active, click to activate
        logg.debug("Card view wasn't active, clicking to activate.")
        card_btn.click()
    else:
        logg.debug("Card view already active.")

    # Iterate through cards
    for i in range(0, 2):
        # Get the 'done' button
        a.scroll_absolute('up')
        done_btn = a.get_elem('//div[@class="card-options-wrapper"]/*/button[@id="triggerCloseCurtain"]')
        done_btn.click()
        a.rand_wait(a.fast_wait)
        if i == 0:
            # Get the 'next' button
            a.scroll_absolute('up')
            next_btn = a.get_elem('//div[contains(@class, "next-card-btn")]')
            if next_btn is not None:
                logg.debug('Clicking next button')
                next_btn.click()
            else:
                logg.debug('No next button found.')
            a.rand_wait(a.fast_wait)


def financial_wellness():
    fw_url = 'https://www.moneyhabits.co/virginpulse'
    c.get(fw_url)
    a.rand_wait(a.medium_wait)
    budget_url = 'https://www.moneyhabits.co/web-fe/budgeting'
    c.get(budget_url)
    a.rand_wait(a.medium_wait)

    if today.strftime('%d') == 1:
        # First of month, adjust budget
        c.get(budget_url)
        a.click('//div/button[contains(text(), "Set Budget"]')


def fitness_tracker():
    fitness_url = 'https://www.myfitnesspal.com/account/login'
    c.get(fitness_url)
    a.rand_wait(a.medium_wait)
    a.enter('//input[@id="username"]', creds['user'])
    a.enter('//input[@id="password"]', creds['password'])
    a.click('//input[@type="submit"]')
    a.rand_wait(a.medium_wait)

    food_diary_url = 'https://www.myfitnesspal.com/food/diary'
    c.get(food_diary_url)

    # Quick add calories
    quick_add_url = 'https://www.myfitnesspal.com/food/copy_meal?date={:%F}&from_date=2019-01-24&from_meal=0&username=obrock2'.format(today)
    c.get(quick_add_url)
    a.rand_wait(a.medium_wait)


def recipes_section():
    """Go through the recipes section"""
    recipe_url = 'https://member.virginpulse.com/devices/zipongosso'
    c.get(recipe_url)
    a.rand_wait(a.slow_wait)
    # If popup, disable
    try:
        a.scroll_absolute('up')
        pu_get_app = c.find_element_by_xpath('//div[@id="interstitial-content-close"]/span')
        pu_get_app.click()
        logg.debug('Closed popup')
    except:
        logg.debug('No popup to close')

    # Meal buttons to click
    meal_btns = c.find_elements_by_xpath('//button[@class="button-green dash-meal-button"]')
    meal_btns[1].click()

    if today.strftime('%a') == 'Mon':
        logg.info('Performing weekly activities')
        # If a monday, favorite a recipe and add to grocery list
        # Favorite (once weekly)
        logg.info('Favoriting recipe')
        heart = None
        for attempt in range(0, 5):
            try:
                heart = c.find_element_by_xpath('//div[@class="heart"]')
                fav = c.find_element_by_xpath('//div[@class="favorite" and div[@class="heart"]]')
                break
            except:
                logg.info('No heart found. Refreshing.')
                c.refresh()
                a.rand_wait(a.medium_wait)
                pass
        if heart is None:
            logg.info('Could not find the heart element.')
        else:
            heart.click()
            a.rand_wait(a.medium_wait)
        if 'is-favorite' not in fav.get_attribute('class'):
            # Click the heart's parent
            fav.click()

        logg.info('Adding recipe to grocery list')
        # Add to grocery list (once weekly)
        a.click('//div[@class="action-text"]/span[text()="Add to Grocery List"]')
        a.rand_wait(a.medium_wait)
        # Confirm add
        a.scroll_absolute('down')
        a.click('//div[@class="grocery-list-add-modal-confirm-container"]')
        a.rand_wait(a.medium_wait)


def healthy_habits():
    """Scroll through and complete the healthy habits items"""
    hh_url = "https://app.member.virginpulse.com/#/healthyhabits"
    c.get(hh_url)
    yes_btns = c.find_elements_by_xpath('//div/button[contains(@class, "btn-choice-yes")]')

    clicks = 0
    click_limit = 10 # overkill, but we'll keep it
    for i in range(0, len(yes_btns)):
        # In case we get a stale element exception, keep refreshing our yes button inventory
        yes_btns = c.find_elements_by_xpath('//div/button[contains(@class, "btn-choice-yes")]')
        yes_btn = yes_btns[i]
        if clicks > click_limit:
            break
        if 'green-button' not in yes_btn.get_attribute('class'):
            # Button not clicked
            yes_id = yes_btn.get_attribute('id')
            # Scroll to button
            c.execute_script("arguments[0].scrollIntoView();", yes_btn)
            c.execute_script("document.getElementById('{}').click()".format(yes_id))
            logg.debug('Clicked button: {}'.format(yes_id))
            clicks += 1
        a.rand_wait(a.fast_wait)


def whil_session():
    """Go to the WHIL page and play a video"""
    whil_url = "https://connect.whil.com/virginpulsesso/redirect?destination=home"
    c.get(whil_url)

    # Play a specific session
    body_sense_url = "https://connect.whil.com/goaltags/freemium-mindfulness-101/sessions/sense-the-body"
    c.get(body_sense_url)
    a.click('//*/img[@alt="play"]')
    # Wait five-ish mins
    time.sleep(310)


vpulse_home_url = 'https://member.virginpulse.com/'
c.get(vpulse_home_url)
a.rand_wait(a.medium_wait)

a.enter('//input[@id="username"]', creds['user'])
a.enter('//input[@id="password"]', creds['password'])
a.click('//input[@id="kc-login"]')
logg.debug('Logged in.')
a.rand_wait(a.slow_wait)

# Establish an order to go through the different tasks
tasks_dict = OrderedDict((
    ('popup closer', popup_closer),
    ('daily cards', daily_cards),
    ('financial wellness', financial_wellness),
    ('fitness tracker', fitness_tracker),
    ('healthy recipes', recipes_section),
    ('healthy habits', healthy_habits),
    ('WHIL session', whil_session)
))

for task_name, task in tasks_dict.items():
    logg.debug('Beginning {} section.'.format(task_name))
    try:
        task()
    except Exception as e:
        logg.error('An error occurred: {}'.format(e))


logg.debug('Script complete. Quitting instance.')
c.quit()
