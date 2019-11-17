#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from datetime import datetime as dtt
from collections import OrderedDict
from kavalkilu import Log, LogArgParser, Keys, BrowserAction
from slacktools import SlackTools


debug = False
logg = Log('vpulse_auto', log_lvl=LogArgParser().loglvl)
try:
    # Attempt to connect to Slack, don't freak out if we have a connection Error though
    st = SlackTools(logg.log_name)
except TimeoutError:
    st = None

# TODO
# build out a table of when monthly, weekly things were last done.
# Handle weekly tasks either based on DOW or recorded table with date_last_done and freq columns

# Get credentials
creds = Keys().get_key('vpulse_creds')


def notify_channel(msg):
    if st is not None:
        st.send_message('notifications', msg)


def popup_closer():
    # Try to find the popup close button
    try:
        # Scroll back up to the top
        ba.scroll_absolute()
        ba.fast_wait()
        pu_close_btn = ba.get_elem('//div[@id="trophy-modal-close-btn"]')
        pu_close_btn.click()
        logg.debug('Popup close button likely successfully clicked.')
    except:
        logg.debug('Popup close button non-existent, or unable to be clicked.')
        ba.medium_wait()


def daily_cards():
    """Handles the daily cards section"""
    ba.scroll_absolute()
    card_btn = ba.get_elem('//div[@class="home-cards-wrapper"]/div/div[@ng-click="toggleDailyTips()"]')
    # Get the class of the child div
    child_div = card_btn.find_element_by_xpath('.//div')
    if 'active-view' not in child_div.get_attribute('class'):
        # Card view not already active, click to activate
        logg.debug("Card view wasn't active, clicking to activate.")
        card_btn.click()
    else:
        logg.debug("Card view already active.")

    # Iterate through cards (2)
    is_tf_btn = False
    for i in range(0, 2):
        # Get the 'done' button
        ba.scroll_absolute('up')
        done_btn = ba.get_elem('//div[@class="card-options-wrapper"]/*/button[@id="triggerCloseCurtain"]')
        ba.scroll_absolute(dir='0,20')
        if done_btn is None:
            logg.debug('Done button not found. Attempting to find a TF button')
            tf_btns = ba.get_elem('//div[@class="card-options-wrapper"]/*/button', single=False)
            if len(tf_btns) > 0:
                logg.debug('Found {} matching buttons. Using first.'.format(len(tf_btns)))
                done_btn = tf_btns[0]
                is_tf_btn = True
        try:
            done_btn.click()
            logg.debug('Done button most likely clicked.')
        except:
            logg.debug('Done button missing. Trying to click the True button instead.')

        if is_tf_btn:
            # We have one more button to click
            complete_btn = ba.get_elem('//div[@class="card-options-wrapper"]/*/button[@ng-click="completeCard(card)"]')
            try:
                complete_btn.click()
                logg.debug('TF complete button most likely clicked.')
            except:
                logg.debug('TF complete button missing. Wasn\'t able to click it.')

        ba.fast_wait()


def financial_wellness():
    fw_url = 'https://www.moneyhabits.co/virginpulse'
    ba.get(fw_url)
    ba.medium_wait()
    budget_url = 'https://www.moneyhabits.co/web-fe/budgeting'
    ba.get(budget_url)
    ba.medium_wait()

    if today.strftime('%d') == 1:
        # First of month, adjust budget
        ba.get(budget_url)
        ba.click('//div/button[contains(text(), "Set Budget"]')


def fitness_tracker():
    url_dict = {
        'base': 'https://www.myfitnesspal.com',
        'tgt': '2019-01-24',
        'today': today.strftime('%F'),
        'user': 'obrock2'
    }
    # Add in extra url bits
    url_dict['extras'] = 'from_meal=0&username={user}'.format(**url_dict)

    fitness_url = '{base}/account/login'.format(**url_dict)
    ba.get(fitness_url)
    ba.medium_wait()

    ba.enter('//input[@id="username"]', creds['user'])
    ba.enter('//input[@id="password"]', creds['password'])
    ba.click('//input[@type="submit"]')
    ba.medium_wait()

    logg.debug('Going to food diary')
    food_diary_url = '{base}/food/diary'.format(**url_dict)
    ba.get(food_diary_url)

    # Quick add calories
    logg.debug('Copying meal from {tgt} to {today}'.format(**url_dict))
    quick_add_url = '{base}/food/copy_meal?date={today}&from_date={tgt}&{extras}'.format(**url_dict)
    ba.get(quick_add_url)
    ba.medium_wait()


def recipes_section():
    """Go through the recipes section"""
    recipe_url = 'https://member.virginpulse.com/devices/zipongosso'
    ba.get(recipe_url)
    ba.slow_wait()
    # If popup, disable
    try:
        ba.scroll_absolute('up')
        pu_get_app = ba.get_elem('//div[@id="interstitial-content-close"]/span')
        pu_get_app.click()
        logg.debug('Closed popup')
    except:
        logg.debug('No popup to close')

    # Meal buttons to click
    meal_btns = ba.get_elem('//button[@class="button-green dash-meal-button"]', single=False)
    meal_btns[1].click()
    logg.debug('Clicked meal button')
    ba.slow_wait()

    if today.strftime('%a') == 'Mon':
        logg.info('Performing weekly activities')
        # If a monday, favorite a recipe and add to grocery list
        # Favorite (once weekly)
        logg.info('Favoriting recipe')
        heart = None
        for attempt in range(0, 5):
            try:
                heart = ba.get_elem('//div[@class="heart"]')
                fav = ba.get_elem('//div[@class="favorite" and div[@class="heart"]]')
                break
            except Exception as e:
                logg.error_with_class(e, 'No heart found. Refreshing.')
                ba.driver.refresh()
                ba.medium_wait()
        if heart is None:
            logg.info('Could not find the heart element.')
        else:
            heart.click()
            ba.medium_wait()

        if 'is-favorite' not in fav.get_attribute('class'):
            # Click the heart's parent
            logg.debug("Heart click didn't work. Trying to click the favourite button instead.")
            fav.click()
            ba.medium_wait()

        logg.info('Adding recipe to grocery list')
        # Add to grocery list (once weekly)
        ba.scroll_absolute('up')
        ba.click('//div[@class="action-text"]/span[text()="Add to Grocery List"]')
        ba.medium_wait()
        # Confirm add
        ba.scroll_absolute('down')
        ba.click('//div[@class="grocery-list-add-modal-confirm-container"]')
        ba.medium_wait()


def healthy_habits():
    """Scroll through and complete the healthy habits items"""
    hh_url = "https://app.member.virginpulse.com/#/healthyhabits"
    ba.get(hh_url)
    ba.medium_wait()
    yes_btns = ba.get_elem('//div/button[contains(@class, "btn-choice-yes")]', single=False)
    logg.debug('{} yes buttons found.'.format(len(yes_btns)))

    clicks = 0
    click_limit = 10  # overkill, but we'll keep it
    for i in range(0, len(yes_btns)):
        # In case we get a stale element exception, keep refreshing our yes button inventory
        yes_btns = ba.get_elem('//div/button[contains(@class, "btn-choice-yes")]', single=False)
        yes_btn = yes_btns[i]
        yes_id = yes_btn.get_attribute('id')
        if clicks > click_limit:
            logg.debug('Click limit reached. Breaking loop.')
            break
        if 'green-button' not in yes_btn.get_attribute('class'):
            # Button not clicked
            try:
                # Scroll to button
                ba.scroll_to_element(yes_btn)
                # c.execute_script("arguments[0].scrollIntoView();", yes_btn)
                ba.driver.execute_script("document.getElementById('{}').click()".format(yes_id))
                logg.debug('Clicked button: {}'.format(yes_id))
                clicks += 1
            except Exception as e:
                logg.error_with_class(e, 'Tried to click yes_btn.')

        else:
            logg.debug('Button {} seems to have already been clicked.'.format(yes_id))

        ba.medium_wait()


def whil_session():
    """Go to the WHIL page and play a video"""
    whil_url = "https://connect.whil.com/virginpulsesso/redirect?destination=home"
    ba.get(whil_url)
    ba.medium_wait()
    # Play a specific session
    body_sense_url = "https://connect.whil.com/goaltags/freemium-mindfulness-101/sessions/sense-the-body"
    ba.get(body_sense_url)
    ba.medium_wait()
    ba.click('//*/img[@alt="play"]')
    # Wait five-ish mins
    time.sleep(310)


notify_channel('Vpulse script booted up')
today = dtt.today()
ba = BrowserAction('chrome', headless=True)
logg.debug('Chrome instantiated.')

vpulse_home_url = 'https://member.virginpulse.com/'
ba.get(vpulse_home_url)
ba.medium_wait()

ba.enter('//input[@id="username"]', creds['user'])
ba.enter('//input[@id="password"]', creds['password'])
ba.click('//input[@id="kc-login"]')
ba.medium_wait()
# Look for a security check
sec_form = ba.get_elem('//input[@value="Send code"]')
if sec_form is not None:
    notify_channel('Security code was requested. This script will have to be rerun manually later.')
    if debug:
        # Click the button
        sec_form.click()
        sec_code = input('Please input the code you were just emailed: ')
        ba.enter('//input[@id="securityCode"]', sec_code)
        ba.click('//input[@value="Submit"]')

notify_channel('Logged in.')
logg.debug('Logged in.')
ba.slow_wait()

# Establish an order to go through the different tasks
tasks_dict = OrderedDict((
    ('popup closer', popup_closer),
    ('daily cards', daily_cards),
    # ('financial wellness', financial_wellness),
    ('fitness tracker', fitness_tracker),
    ('healthy recipes', recipes_section),
    ('healthy habits', healthy_habits),
    ('WHIL session', whil_session)
))

for task_name, task in tasks_dict.items():
    logg.debug('Beginning {} section.'.format(task_name))
    try:
        task()
        notify_channel('Completed section: {}'.format(task_name))
    except Exception as e:
        err_msg = 'Error occurred in section: {}'.format(task_name)
        logg.error_with_class(e, err_msg)
        notify_channel(err_msg)

logg.debug('Script complete. Quitting instance.')
ba.tear_down()
notify_channel('Competed script.')
logg.close()
