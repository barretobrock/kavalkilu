#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from datetime import timedelta as tdelta
import re
import time
import pandas as pd
from tabulate import tabulate
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
        - `time`
        - `look (left|right|up|down)`
        - `oof`
        - `wink wink`
        - `bruh`
        - `access <literally-anything-else>`
    *Useful commands:*
        - `garage`: current snapshot of garage
        - `garage door status`: whether or not the door is open
        - `lights status`: status of all connected lights
        - `lights turn on|off <light>`: turn on/off selected light
        - `temps`: temperatures of all sensor stations
        - `uptime`: printout of devices' current uptime
        - `channel stats`: get a leaderboard of the last 1000 messages posted in the channel
    """

    commands = {
        'speak': 'woof',
        'good bot': 'thanks!',
        'hello': 'Hi <@{user}>!',
    }

    sarcastic_reponses = [
        ''.join([':ah-ah-ah:'] * randint(0, 50)),
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
            self.send_message('notifications', 'Rebooted and ready to party! :tada:')
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
        elif message == 'look left':
            fpath = os.path.join(os.path.expanduser('~'), *['Pictures', 'look-left.jpg'])
            self.upload_file(channel, fpath, 'whatamilookingfor.png')
        elif message == 'look right':
            fpath = os.path.join(os.path.expanduser('~'), *['Pictures', 'look-right.jpg'])
            self.upload_file(channel, fpath, 'whatamilookingfor.png')
        elif message == 'look up':
            fpath = os.path.join(os.path.expanduser('~'), *['Pictures', 'look-up.jpg'])
            self.upload_file(channel, fpath, 'whatamilookingfor.png')
        elif message == 'look down':
            fpath = os.path.join(os.path.expanduser('~'), *['Pictures', 'look-down.jpg'])
            self.upload_file(channel, fpath, 'whatamilookingfor.png')
        elif message == 'oof':
            fpath = os.path.join(os.path.expanduser('~'), *['Pictures', 'oof.jpg'])
            self.upload_file(channel, fpath, 'oof')
        elif message == 'wink wink':
            fpath = os.path.join(os.path.expanduser('~'), *['Pictures', 'wink.jpg'])
            self.upload_file(channel, fpath, ':smirk:')
        elif message == 'bruh':
            fpath = os.path.join(os.path.expanduser('~'), *['Pictures', 'shock.jpg'])
            self.upload_file(channel, fpath, 'omg')
        elif message == 'time':
            response = 'The time is {:%F %T}'.format(dt.today())
        elif message == 'uptime':
            try:
                response = self.get_uptime()
            except Exception as e:
                response = 'I tried, but I could not retrieve that info! \nError: {}'.format(e)
        elif message == 'garage door status':
            response = self.get_garage_status()
        elif message == 'temps':
            response = self.get_temps()
        elif message == 'channel stats':
            response = self.get_channel_stats(channel)
        elif message.startswith('lights'):
            # lights (status|turn (on|off) <light_name>)
            if user not in approved_users:
                response = self.sarcastic_reponses[randint(0, len(self.sarcastic_reponses) - 1)]
            else:
                response = self.light_actions(message)
        elif message.startswith('access'):
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

    def df_to_slack_table(self, df):
        """Takes in a dataframe, outputs a string formatted for Slack"""
        return tabulate(df, headers='keys', tablefmt='github', showindex='never')

    def get_channel_stats(self, channel):
        """Collects posting stats for a given channel"""
        resp = self.user.api_call(
            'channels.history',
            channel=channel,
            count=1000
        )

        if resp['ok']:
            results = {}

            msgs = resp['messages']
            for msg in msgs:
                try:
                    user = msg['user']
                except KeyError:
                    user = msg['bot_id']
                txt_len = len(msg['text'])
                if user in results.keys():
                    results[user]['msgs'].append(txt_len)
                else:
                    # Apply new dict for new user
                    results[user] = {'msgs': [txt_len]}
        else:
            return "Oops - there was an error in the API call for this :shrugman:"

        # Process messages
        for k, v in results.items():
            results[k] = {
                'total_messages': len(v['msgs']),
                'avg_msg_len': sum(v['msgs']) / len(v['msgs'])
            }

        res_df = pd.DataFrame(results).transpose()

        res_df = res_df.reset_index()
        res_df = res_df.rename(columns={'index': 'user'})
        res_df['user'] = res_df['user'].apply(lambda x: '<@{}>'.format(x))
        res_df['total_messages'] = res_df['total_messages'].astype(int)
        res_df['avg_msg_len'] = res_df['avg_msg_len'].round(1)
        res_df = res_df.sort_values('total_messages', ascending=False)
        response = '*Stats for this channel:*\n Total messages examined: {}\n' \
                   '```{}```'.format(len(msgs), self.df_to_slack_table(res_df))
        return response

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
        response = '*Device Uptime:*\n```{}```'.format(self.df_to_slack_table(uptime))
        return response

    def get_temps(self):
        """Gets device temperatures"""
        eng = MySQLLocal('homeautodb')

        temp_query = """
            SELECT
                l.location
                , temps.record_value AS value
                , temps.record_date
            FROM (
                SELECT
                    loc_id
                    , MAX(record_date) AS most_recent
                FROM
                    homeautodb.temps AS t
                GROUP BY
                    loc_id
                ) AS latest_reads
            INNER JOIN
              homeautodb.temps
            ON
              temps.loc_id = latest_reads.loc_id AND
              temps.record_date = latest_reads.most_recent
            LEFT JOIN homeautodb.locations AS l ON temps.loc_id = l.id
            WHERE
                l.location != 'test'
        """
        temps = pd.read_sql_query(temp_query, eng.connection)

        today = pd.datetime.today()
        for i, row in temps.iterrows():
            if not pd.isnull(row['record_date']):
                datediff = reldelta(today, pd.to_datetime(row['record_date']))
                datediff = DateTools().human_readable(datediff)
            else:
                datediff = 'unknown'
            temps.loc[i, 'ago'] = datediff

        temps = temps[['location', 'value', 'ago']]
        response = '*Most Recent Temperature Readings:*\n```{}```'.format(self.df_to_slack_table(temps))
        return response

    def get_garage_status(self):
        """Gets device uptime for specific devices"""
        eng = MySQLLocal('homeautodb')

        garage_status_query = """
            SELECT
                d.name
                , d.status
                , d.status_chg_date
                , d.update_date
            FROM
                doors AS d
            WHERE
                name = 'garage'
        """
        garage_status = pd.read_sql_query(garage_status_query, con=eng.connection)
        status_dict = {k: v[0] for k, v in garage_status.to_dict().items()}
        response = "*Current Status*: `{status}`\n *Changed at*:" \
                   " `{status_chg_date:%F %T}`\n *Updated*: `{update_date:%F %T}`".format(**status_dict)
        return response
