#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import mimetypes
from smtplib import SMTP
import datetime
from datetime import datetime as dt
from datetime import timedelta as tdelta
import os
import re
import time
import socket
import pandas as pd
from dateutil.relativedelta import relativedelta as reldelta
from random import randint
from .camera import Amcrest
from .light import HueBulb, hue_lights
from .net import Hosts, Keys
from .databases import MySQLLocal
from .date import DateTools


class SlackBot:
    """Handles messaging to and from Slack API"""

    help_txt = """
    I'm Viktor. Here's what I can do:
    *Basic Commands:*
        - `hello`
        - `speak`
        - `good bot`
        - `fuck`
        - `time`
        - `access main ...`
    *Useful commands:*
        - `garage`: current snapshot of garage
        - `garage door status`: whether or not the door is open
        - `lights status`: status of all connected lights
        - `lights turn on|off <light>`: turn on/off selected light
        - `temps`: temperatures of all sensor stations
        - `uptime`: printout of devices' current uptime
    """

    commands = {
        'speak': 'woof',
        'good bot': 'thanks!',
        'hello': 'Hi <@{user}>!',
        'fuck': 'Watch yo profanity! https://www.youtube.com/watch?v=hpigjnKl7nI',
    }

    sarcastic_reponses = [
        ''.join([':ah-ah-ah:'] * 50),
        'Lol <@{user}>... here ya go bruv :pick:',
        'Nah boo, we good.',
        'Yeah, how about you go on ahead and, you know, do that yourself.'
        ':bye_felicia:'
    ]

    def __init__(self):
        slack = __import__('slackclient')
        bot_token = Keys().get_key('kodubot-useraccess')
        user_token = Keys().get_key('kodubot-usertoken')
        self.client = slack.SlackClient(bot_token)
        self.user = slack.SlackClient(user_token)
        self.kodubot_id = None
        self.RTM_READ_DELAY = 1
        self.MENTION_REGEX = "^(<@(|[WU].+?)>|v!)(.*)"

    def run_rtm(self):
        """Initiate real-time messaging"""
        if self.client.rtm_connect(with_team_state=False):
            print('Viktor is running!')
            self.kodubot_id = self.client.api_call('auth.test')['user_id']
            while True:
                try:
                    msg_packet = self.parse_bot_commands(self.client.rtm_read())
                    if msg_packet is not None:
                        # print('I got a message "{message}" from user: {user} '.format(**msg_packet))
                        self.handle_command(**msg_packet)
                    time.sleep(self.RTM_READ_DELAY)
                except Exception as e:
                    print('Reconnecting... {}'.format(e))
                    self.client.rtm_connect(with_team_state=False)
        else:
            print('Connection failed.')

    def parse_direct_mention(self, message):
        """Parses user and other text from direct mention"""
        matches = re.search(self.MENTION_REGEX, message)
        if matches is not None:
            if matches.group(1).lower() == 'v!':
                # Addressed Viktor using shortened syntax
                user_id = matches.group(1).lower()
            else:
                # Getting viktor's real user id
                user_id = matches.group(2)
            message_txt = matches.group(3).lower().strip()
            return user_id, message_txt
        return None, None

    def parse_bot_commands(self, slack_events):
        """Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event['type'] == 'message' and "subtype" not in event:
                user_id, message = self.parse_direct_mention(event['text'])
                # message = event['text'].lower()
                if user_id in [self.kodubot_id, 'v!']:
                    return {
                        'user': event['user'],
                        'channel': event['channel'],
                        'message': message.strip()
                    }
        return None

    def handle_command(self, channel, message, user):
        """Handles a bot command if it's known"""
        # Users that get to use higher-level actions
        approved_users = ['UM35HE6R5', 'UM3E3G72S']
        response = None
        if message in self.commands.keys():
            response = self.commands[message]
        elif message == 'garage':
            if user not in approved_users:
                response = self.sarcastic_reponses[randint(0, len(self.sarcastic_reponses) - 1)]
            else:
                self.take_garage_pic(channel, user)
                response = 'There ya go!'
        elif message == 'help':
            response = self.help_txt
        elif message == 'time':
            response = 'The time is {:%F %T}'.format(dt.today())
        elif message == 'uptime':
            try:
                response = self.get_uptime()
            except Exception as e:
                response = 'I tried, but I could not retrieve that info! \nError: {}'.format(e)
        elif message == 'garage door status':
            response = 'Coming soon!'
        elif message == 'temps':
            response = 'Coming soon!'
        elif message.startswith('lights'):
            # lights (status|turn (on|off) <light_name>)
            if user not in approved_users:
                response = self.sarcastic_reponses[randint(0, len(self.sarcastic_reponses) - 1)]
            else:
                response = self.light_actions(message)
        elif 'access main' in message:
            response = ''.join([':ah-ah-ah:'] * randint(5, 50))
        elif message != '':
            response = "I didn't understand this: `{}`\n " \
                       "Use `v!help` to get a list of my commands.".format(message)

        if response is not None:
            resp_dict = {
                'user': user
            }
            self.send_message(channel, response.format(**resp_dict))

    def send_message(self, channel, message):
        """Sends a message to the specific channel"""
        self.client.api_call(
            'chat.postMessage',
            channel=channel,
            text=message
        )

    def delete_message(self, message_dict):
        """Deletes a given message"""
        self.user.api_call(
            'chat.delete',
            channel=message_dict['channel']['id'],
            ts=message_dict['ts']
        )

    def search_messages_by_date(self, channel, from_date, date_format='%Y-%m-%d %H:%M', max_results=100):
        """Search for messages in a channel after a certain date

        Args:
            channel: str, the channel (e.g., "#channel")
            from_date: str, the date from which to begin collecting channels
            date_format: str, the format of the date entered
            max_results: int, the maximum number of results per page to return

        Returns: list of dict, channels matching the query
        """
        from_date = dt.strptime(from_date, date_format)
        # using the 'after' filter here, so take it back one day
        slack_date = from_date - tdelta(days=1)

        for attempt in range(3):
            resp = self.user.api_call(
                'search.messages',
                query='in:{} after:{:%F}'.format(channel, slack_date),
                count=max_results
            )
            if resp['ok']:
                # Search was successful
                break
            else:
                # Wait before retrying
                print('Call failed. Waiting two seconds')
                time.sleep(2)

        if 'messages' in resp.keys():
            msgs = resp['messages']['matches']
            filtered_msgs = []
            for msg in msgs:
                # Append the message as long as it's timestamp is later or equal to the time entered
                ts = dt.fromtimestamp(int(round(float(msg['ts']), 0)))
                if ts >= from_date:
                    filtered_msgs.append(msg)
            return filtered_msgs

        return None

    def upload_file(self, channel, filepath, filename):
        """Uploads the selected file to the given channel"""
        self.client.api_call(
            'files.upload',
            channels=channel,
            filename=filename,
            file=open(filepath, 'rb')
        )

    def take_garage_pic(self, channel, user):
        """Takes snapshot of garage, sends to Slack channel"""
        # Take a snapshot of the garage
        garage_cam_ip = Hosts().get_host('ac_garage')['ip']
        creds = Keys().get_key('webcam_api')
        cam = Amcrest(garage_cam_ip, creds)
        tempfile = '/tmp/garagesnap.jpg'
        cam.camera.snapshot(channel=0, path_file=tempfile)
        self.upload_file(channel, tempfile, 'garage_snapshot_{:%F %T}.jpg'.format(dt.today()))

    def light_actions(self, packet):
        """Performs various light-related actions

        Args:
            packet: str, what action to perform
                syntax: "lights (status|turn (on|off) <light_name>)"

        """
        light_names = [x['hue_name'].lower() for x in hue_lights]
        packet_split = packet.strip().split()
        action = packet_split[1]
        if len(packet_split) > 3:
            device = ' '.join(packet_split[3:])
        else:
            device = None

        if action == 'status':
            # Get the status of all the lights
            light_statuses = []
            for light in hue_lights:
                obj = None
                for attempt in range(3):
                    try:
                        obj = HueBulb(light['hue_name'])
                        print('Got {hue_name}'.format(**light))
                        break
                    except Exception as e:
                        print('Waiting... {}'.format(e))
                        time.sleep(1)
                if obj is not None:
                    light_statuses.append({
                        'name': light['hue_name'],
                        'status': 'ON' if obj.get_status() else 'OFF'
                    })
            if len(light_statuses) > 0:
                response = ':bulb:*Here are the current statuses for the lights:*\n'
                response += '\n'.join(['{name:<15}: {status}'.format(**x) for x in light_statuses])
                return response
        elif action.startswith('turn'):
            # Make sure the input name matches the names allowed.
            if device in light_names:
                action_split = action.split()
                # Get the "proper" casing of the light name, as we've forced lower case here
                proper_light_name = hue_lights[light_names.index(device)]['hue_name']
                target_light = None
                for attempt in range(3):
                    try:
                        target_light = HueBulb(proper_light_name)
                        break
                    except Exception as e:
                        time.sleep(1)
                if target_light is None:
                    response = "Sorry, I tried three times to turn on the light and I couldn't do it!"
                elif action_split[1] == 'on':
                    # Proceed with turning on
                    try:
                        target_light.turn_on()
                        response = 'Turned {} ON'.format(device)
                    except Exception as e:
                        response = 'Failed to turn {} ON. Error: {}'.format(device, e)
                elif action_split[1] == 'off':
                    try:
                        target_light.turn_off()
                        response = 'Turned {} OFF'.format(device)
                    except Exception as e:
                        response = 'Failed to turn {} OFF. Error: {}'.format(device, e)
                else:
                    response = 'Did not recognize command {}'.format(action_split[1].upper())
            else:
                # Respond with error and list of all possible lights
                response = '{} is an unrecognized light. Known lights: {}'.format(device, ', '.join(light_names))
            return response

    def get_uptime(self):
        """Gets device uptime for specific devices"""
        eng = MySQLLocal('logdb')

        uptime_query = """
        SELECT
            d.name
            , d.status
            , d.uptime_since
        FROM
            devices AS d
        """
        uptime = pd.read_sql_query(uptime_query, con=eng.connection)

        today = pd.datetime.today()

        for i, row in uptime.iterrows():
            if not pd.isnull(row['uptime_since']):
                datediff = reldelta(today, pd.to_datetime(row['uptime_since']))
                datediff = DateTools().human_readable(datediff)
            else:
                datediff = 'unknown'
            uptime.loc[i, 'uptime'] = datediff
        uptime = uptime[['name', 'uptime']]
        uptime['name'] = uptime['name'].apply(lambda x: '{:>10}'.format(x))
        uptime['uptime'] = uptime['uptime'].apply(lambda x: '{:>20}'.format(x))
        response = '*Device Uptime:*\n```{}```'.format(uptime.to_string(index=False))
        return response

    def get_temps(self):
        """Gets device temperatures"""
        eng = MySQLLocal('homeautodb')

        temp_query = """
        WITH ranked_temps AS (
            SELECT
                l.location AS loc
                , t.record_date AS ts
                , t.record_value AS temp_c
            FROM
                temps AS t
            JOIN
                locations AS l ON l.id = t.loc_id
            WHERE
                l.location != 'test'
        )
        SELECT * FROM ranked_temps WHERE rn = 1
        """

        temps = pd.read_sql_query(temp_query, eng.connection)

class Email:
    """
    Performs email-related activities
    """
    def __init__(self, un, pw, log):
        """Connect to account"""
        self.un = un
        self.pw = pw
        self.log = log
        self.smtpserver = SMTP('smtp.gmail.com', 587)
        self.imapserver = imaplib.IMAP4_SSL('imap.gmail.com', imaplib.IMAP4_SSL_PORT)

    def connect_for_sending(self):
        """Connect to the SMTP server for sending emails"""
        self.smtpserver.ehlo()
        self.smtpserver.starttls()
        self.smtpserver.login(self.un, self.pw)
        self.log.debug('Connected with email server.')

    def connect_for_reading(self):
        """Connect to the IMAP server to read emails"""
        self.imapserver.login(self.un, self.pw)

    def search(self, label='inbox', mail_filter='ALL'):
        """Get email objects based on a filter"""
        self.connect_for_reading()
        self.imapserver.select(label)
        mail_status, mail_data = self.imapserver.uid('search', None, mail_filter)
        # Convert list of ids from bytes to string, then split
        mail_ids = mail_data[0].decode('utf8').split(' ')
        # Get most recent message and check the date
        mail_id = mail_ids[-1]
        email_status, email_data = self.imapserver.uid('fetch', mail_id, "(RFC822)")
        raw_email = email_data[0][1]
        # Parse email from bytes into EmailMessage object for easy data extraction
        emailobj = email.message_from_bytes(raw_email)
        # Check if data of email object was today
        emaildate = datetime.datetime.strptime(emailobj['Date'][:-6], '%a, %d %b %Y %H:%M:%S')
        today = datetime.datetime.now()
        if emaildate.timestamp() > today.timestamp():
            # Email is current. Return elements
            return emailobj

    def forward(self, email_to, email_object):
        """Command to forward an email"""
        email_object.replace_header('From', self.un)
        email_object.replace_header('To', email_to)
        self.log.debug('Communicating with server.')
        try:
            self.connect_for_sending()
            self.smtpserver.sendmail(self.un, email_to, email_object.as_string())
            self.log.debug('Message sent.')
            self.smtpserver.quit()
        except TimeoutError:
            self.log.exception('Connection with server timed out.')
        except:
            self.log.exception('Could not connect with email server.')

    def send(self, email_to, subject, body, attachment_paths=[]):
        """Command to package and send email"""
        self.log.debug('Beginning email process.')
        msg = MIMEMultipart()
        msg["From"] = self.un
        msg["To"] = ', '.join([email_to])
        msg["Subject"] = subject
        msg.preamble = body
        if len(attachment_paths) > 0:
            self.log.debug('Encoding any attachments')
            for attachment_path in attachment_paths:
                ctype, encoding = mimetypes.guess_type(attachment_path)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                if maintype == 'text':
                    with open(attachment_path) as f:
                        attachment = MIMEText(f.read(), _subtype=subtype)
                else:
                    with open(attachment_path) as f:
                        attachment = MIMEBase(maintype, subtype)
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                attachment.add_header("Content-Disposition", 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(attachment)
        self.log.debug('Communicating with server.')
        try:
            self.connect_for_sending()
            self.smtpserver.sendmail(self.un, email_to, msg.as_string())
            self.log.debug('Message sent.')
            self.smtpserver.quit()
        except TimeoutError:
            self.log.exception('Connection with server timed out.')
        except:
            self.log.exception('Could not connect with email server.')


class PBullet:
    """
    Connects to Pushbullet API
    Args for __init__:
        api: str, Pushbullet API key
    """
    def __init__(self, api):
        self.pushbullet = __import__('pushbullet')

        self.api = api
        self.pb = self.pushbullet.PushBullet(self.api)

    def send_message(self, title, message):
        """Sends a message"""
        self.pb.push_note(title, message)

    def send_address(self, title, address):
        """Sends an address"""
        self.pb.push_address(title, address)

    def send_link(self, text, link):
        """Sends a link"""
        self.pb.push_link(text, link)

    def send_img(self, filepath, title, filetype='image/png'):
        """Sends an image"""
        with open(filepath, 'rb') as thing:
            file_data = self.pb.upload_file(thing, title, file_type=filetype)
        push = self.pb.push_file(**file_data)


class INET:
    """
    Performs variety of internet connection tests
    """
    def __init__(self):
        pass

    def get_ip_address(self):
        """Retrieves the local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except:
            return ''

    def ping_success(self, is_internal=False):
        """
        Checks if connected to internet
        Args:
            is_internal: boolean, pings internal network if True. default False
        """
        if is_internal:
            host = "192.168.0.1"
        else:
            host = "8.8.8.8"
        response = os.system("ping -c 1 {}".format(host))
        if response == 0:
            return True
        else:
            return False


class TWAPI:
    def __init__(self):
        self.API = __import__('tweepy').API


class Twitter(TWAPI):
    def __init__(self, key_dict):
        self.twp = __import__('tweepy')
        # Import keys
        self.CONSUMER_KEY = key_dict['consumer_key']
        self.CONSUMER_SECRET = key_dict['consumer_secret']
        self.ACCESS_KEY = key_dict['access_key']
        self.ACCESS_SECRET = key_dict['access_secret']
        auth = self.twp.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        auth.set_access_token(self.ACCESS_KEY, self.ACCESS_SECRET)
        super(Twitter, self).__init__(auth)

    def get_messages(self):
        msgs = self.direct_messages()
        return msgs

    def get_followers(self):
        followers = self.followers()
        return followers

    def post(self, text, log=None, char_limit=140):
        if text != "":
            if len(text) > char_limit:
                text = text[:char_limit]
            try:
                self.update_status(status=text)
            except:
                if log is not None:
                    log.exception('Failed to post tweet.')
                else:
                    raise ValueError('Tweet failed to post!')
                    pass

    def send_message(self, user_id, text):
        if text != "":
            self.send_direct_message(user_id=user_id, text=text)

    def delete_tweet(self, datetime_lim, containing=""):
        timeline = self.twp.Cursor(self.user_timeline).items()
        for tweet in timeline:
            if tweet.created_at < datetime_lim:
                if containing != "":
                    if containing in tweet.text:
                        print("Destroying {}\n{}".format(tweet.id, tweet.text))
                        self.destroy_status(tweet.id)
                else:
                    print("Destroying {}\n{}".format(tweet.id, tweet.text))
                    self.destroy_status(tweet.id)

