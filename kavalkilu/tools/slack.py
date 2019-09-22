#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from datetime import timedelta as tdelta
import re
import time
import requests
import string
import pandas as pd
from tabulate import tabulate
from dateutil.relativedelta import relativedelta as reldelta
from random import randint
from .camera import Amcrest
from .light import HueBulb, hue_lights
from .net import Hosts, Keys
from .databases import MySQLLocal
from .date import DateTools
from .text import MarkovText, TextCleaner, WebExtractor


class SlackBot:
    """Handles messaging to and from Slack API"""

    help_txt = """
    I'm Viktor. Here's what I can do:
    *Basic Commands:*
        - `hello`
        - `speak`
        - `good bot`
        - `thanks`
        - `no, thank you`
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
        - `emojis like <regex-pattern>`: get emojis matching the regex pattern
        - `(make sentences|ms) <url1> <url2`: reads in text from the given urls, tries to generate up to 5 sentences
        - `acro-guess <acronym> [-f|-i]`: there are a lot of acronyms at work. this tries to guess what it means.
        - `insult <thing|person>`: generates an insult
        - `quote me <thing-to-quote>`: turns your phrase into letter emojis
    """

    commands = {
        'speak': 'woof',
        'good bot': 'thanks <@{user}>!',
        'hello': 'Hi <@{user}>!',
        'thanks': 'No, thank you!',
        'no, thank you': 'No, no, thank you!',
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
        # Key starting with 'xoxb...'
        bot_token = Keys().get_key('kodubot-useraccess')
        self.bot = slack.SlackClient(bot_token)
        # Key starting with 'xoxp...'
        user_token = Keys().get_key('kodubot-usertoken')
        self.user = slack.SlackClient(user_token)
        self.kodubot_id = None
        self.RTM_READ_DELAY = 1
        self.MENTION_REGEX = "^(<@(|[WU].+?)>|[vV]!)(.*)"
        team_name = Keys().get_key('okr-name')
        self.st = SlackTools(team_name, user_token)

    def run_rtm(self):
        """Initiate real-time messaging"""
        if self.bot.rtm_connect(with_team_state=False):
            print('Viktor is running!!')
            self.kodubot_id = self.bot.api_call('auth.test')['user_id']
            self.send_message('notifications', 'Rebooted and ready to party! :tada:')
            while True:
                try:
                    msg_packet = self.parse_bot_commands(self.bot.rtm_read())
                    if msg_packet is not None:
                        # print('I got a message "{message}" from user: {user} '.format(**msg_packet))
                        self.handle_command(**msg_packet)
                    time.sleep(self.RTM_READ_DELAY)
                except Exception as e:
                    print('Reconnecting... {}'.format(e))
                    self.bot.rtm_connect(with_team_state=False)
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
        elif message.startswith('make sentences') or message.startswith('ms '):
            try:
                response = self.generate_sentences(message)
            except Exception as e:
                response = 'I tried that and got an error: ```{}```'.format(e)
        elif message.startswith('acro-guess'):
            response = self.guess_acronym(message)
        elif message.startswith('insult'):
            response = self.insult(message)
        elif message.startswith('emojis like'):
            response = self.get_emojis_like(message)
        elif message.startswith('lights'):
            # lights (status|turn (on|off) <light_name>)
            if user not in approved_users:
                response = self.sarcastic_reponses[randint(0, len(self.sarcastic_reponses) - 1)]
            else:
                response = self.light_actions(message)
        elif message.startswith('no') and any([x in message for x in ['thank you', 'thanks', 'tanks']]):
            response = self.overly_polite(message)
        elif message.startswith('access'):
            response = ''.join([':ah-ah-ah:'] * randint(5, 50))
        elif message.startswith('quote me'):
            msg = message[len('quote me'):].strip()
            response = self.st.build_phrase(msg)
        elif message != '':
            response = "I didn't understand this: `{}`\n " \
                       "Use `v!help` to get a list of my commands.".format(message)

        if response is not None:
            resp_dict = {
                'user': user
            }
            self.send_message(channel, response.format(**resp_dict))

    def get_channel_members(self, channel, humans_only=False):
        """Collect members of a particular channel
        Args:
            channel: str, the channel to examine
            humans_only: bool, if True, will only return non-bots in the channel
        """
        resp = self.bot.api_call(
            'conversations.members',
            channel=channel
        )
        if resp['ok']:
            users = resp['members']
            target_data = ['id', 'name', 'real_name', 'is_bot']
            users = [{x: user[x] for x in target_data} for user in self.get_users_info(users)]

            if humans_only:
                humans = [user for user in users if not user['is_bot']]
                return humans
            else:
                return users
        return None

    def private_channel_message(self, user_id, channel, message):
        """Send a message to a user on the channel"""
        resp2 = self.bot.api_call(
            'chat.postEphemeral',
            channel=channel,
            user=user_id,
            text=message
        )
        if not resp2['ok']:
            raise Exception(resp2['error'])

    def private_message(self, user_id, message):
        """Send private message to user"""
        resp = self.bot.api_call(
            'im.open',
            user=user_id,
        )

        if resp['ok']:
            resp2 = self.bot.api_call(
                'chat.postMessage',
                channel=resp['channel']['id'],
                text=message
            )
            if not resp2['ok']:
                raise Exception(resp2['error'])

    def get_users_info(self, user_list):
        """Collects info from a list of user ids"""
        user_info = []
        for user in user_list:
            resp = self.bot.api_call(
                'users.info',
                user=user
            )
            if resp['ok']:
                user_info.append(resp['user'])
        return user_info

    def send_message(self, channel, message):
        """Sends a message to the specific channel"""
        self.bot.api_call(
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
        self.bot.api_call(
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
        user_names = pd.DataFrame(self.get_users_info(res_df['user'].tolist()))[['id', 'real_name']]
        res_df = res_df.merge(user_names, left_on='user', right_on='id', how='left').drop(['user', 'id'], axis=1)
        res_df = res_df[['real_name', 'total_messages', 'avg_msg_len']]
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

    def get_emojis_like(self, message, max_res=500):
        """Gets emojis matching in the system that match a given regex pattern"""

        # Parse the regex from the message
        ptrn = re.search(r'(?<=emojis like ).*', message)
        if ptrn.group(0) != '':
            # We've got a pattern to use
            pattern = re.compile(ptrn.group(0))
            resp = self.user.api_call('emoji.list')
            if resp['ok']:
                emojis = resp['emoji']
                matches = [k for k, v in emojis.items() if pattern.match(k)]
                len_match = len(matches)
                if len_match > 0:
                    # Slack apparently handles message length limitations on its end, so
                    #   let's just put all the emojis together into one string
                    response = ''.join([':{}:'.format(x) for x in matches[:max_res]])
                else:
                    response = 'No results for pattern `{}`'.format(ptrn.group(0))

                if len_match >= max_res:
                    # Append to the emoji_str that it was truncated
                    response = '`**Truncated Results ({}) -> ({})**'.format(len_match, max_res, response)
            else:
                response = 'Oopsies, something went wrong.'
        else:
            response = "I couldn't find a pattern from your message. Get your shit together <@{user}>"
        return response

    def generate_sentences(self, message):
        """Builds a Markov chain from some text sources"""
        # Parse out urls
        msg_split = message.split(' ')
        matches = [x for x in msg_split if re.search(r'http[s]?:\/\/\S+', x) is not None]

        if len(matches) > 0:
            # We've got some urls. Make sure we limit it to 5 in case someone's greedy
            urls = matches[:4]
            we = WebExtractor()
            cleaner = TextCleaner()
            clean_list = []
            for url in urls:
                # Collect HTML elements
                # Slack adds '<' and '>' to the urls. Remove them
                url = re.sub(r'[<>]', '', url)
                elems = we.get_matching_elements(url, ['li', 'p', 'span'])
                # Extract text from tags
                txt_list = []
                for elem in elems:
                    try:
                        elemtxt = elem.get_text()
                        # Try to take out any CSS / javascript that may have gotten in
                        # elemtxt = re.sub(r'(function\s+\w+\(.*\};?|\{.*\})', '', elemtxt)
                        if len(re.sub('[.,\/#!$%\^&\*;:{}=\-`~()]', '', elemtxt).split(' ')) >= 5:
                            txt_list.append(elemtxt)
                    except AttributeError:
                        pass
                cleaned = ''.join([cleaner.process_text(x) for x in txt_list])
                clean_list.append(cleaned)

            mkov = MarkovText(clean_list)
            sentences = []
            for attempt in range(5):
                try:
                    sentences = mkov.generate_n_sentences(5)
                    if len(sentences) > 0:
                        break
                except TypeError:
                    pass

            if len(sentences) > 0:
                # Join them and send them
                return '\n---\n'.join(sentences)
            else:
                return "Hmmm. I wasn't able to make any sense of these urls. I might need a larger text source." \
                       " Also make sure the text falls in either a 'li', 'p' or 'span' element."
        else:
            return "I didn't find a url to use from that text."

    def guess_acronym(self, message):
        """Tries to guess an acronym from a message"""
        message_split = message.split()
        if len(message_split) <= 1:
            response = "I can't work like this! I need a real acronym!!:ragetype:"
        # We can work with this
        acronym = message_split[1]
        # clean of any punctuation
        acronym = re.sub(r'\W', '', acronym)

        # Determine which file to use
        file = 'en.txt'
        if len(message_split) > 2:
            if message_split[2] == '-f':
                file = 'en_nsfw.txt'
            elif message_split[2] == '-i':
                file = 'indeed_words.txt'

        # Load the massive list of words
        with open(os.path.join(os.path.expanduser('~'), *['Downloads', file])) as f:
            words = f.readlines()

        # Put the words into a dictionary, classified by first letter
        a2z = string.ascii_lowercase
        word_dict = {k: [] for k in a2z}
        for word in words:
            word = word.replace('\n', '')
            if len(word) > 1:
                word_dict[word[0].lower()].append(word.lower())

        # Build out the real acryonym meaning
        guesses = []
        for guess in range(3):
            meaning = []
            for letter in list(acronym):
                if letter.isalpha():
                    word_list = word_dict[letter]
                    meaning.append(word_list[randint(0, len(word_list) - 1)])
                else:
                    meaning.append(letter)
            guesses.append(' '.join(list(map(str.title, meaning))))

        return ':okily-dokily: Here are my guesses for *{}*!\n {}'.format(acronym, '\n_OR_\n'.join(guesses))

    def insult(self, message):
        """Insults the user at their request"""
        message_split = message.split()
        if len(message_split) <= 1:
            response = "I can't work like this! I need something to insult!!:ragetype:"
            return response
        target = message_split[1]
        f_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        insults = []
        # Load the insults
        for part in ['a', 'b', 'c']:
            with open(os.path.join(f_dir, 'insults_{}.txt'.format(part))) as f:
                insult_list = [x.replace('\n', '') for x in f.readlines()]
            insults.append(insult_list[randint(0, len(insult_list) - 1)])
        if target == 'me':
            return "You're nothing but a {}".format(' '.join(insults))
        else:
            return "That there {} is a no good, {}".format(target, ' '.join(insults))

    def overly_polite(self, message):
        """Responds to 'no, thank you' with an extra 'no' """
        # Count the 'no's
        no_cnt = message.count('no')
        no_cnt += 1
        response = '{}, thank you!'.format(', '.join(['no'] * no_cnt)).capitalize()
        return response


class SlackTools:
    """Tools to make working with Slack better"""

    def __init__(self, team, token, cookie=''):
        slack = __import__('slackclient')
        self.team = team
        self.cookie = cookie
        self.token = token
        self.bot = slack.SlackClient(self.token)
        self.session = self._init_session()

    def _init_session(self):
        """Initialises a session for use with special API calls not allowed through the python package"""
        base_url = 'https://{}.slack.com'.format(self.team)

        session = requests.session()
        session.headers = {'Cookie': self.cookie}
        session.url_customize = '{}/customize/emoji'.format(base_url)
        session.url_add = '{}/api/emoji.add'.format(base_url)
        session.url_list = '{}/api/emoji.adminList'.format(base_url)
        session.api_token = self.token
        return session

    def _upload_emoji(self, filepath):
        """Uploads an emoji to the workspace
        NOTE: The name of the emoji is taken from the filepath
        """
        filename = os.path.split(filepath)[1]
        emoji_name = os.path.splitext(filename)[0]
        data = {
            'mode': 'data',
            'name': emoji_name,
            'token': self.session.api_token
        }
        files = {'image': open(filepath, 'rb')}
        r = self.session.post(self.session.url_add, data=data, files=files, allow_redirects=False)
        r.raise_for_status()

        # Slack returns 200 OK even if upload fails, so check for status.
        response_json = r.json()
        if not response_json['ok']:
            print("Error with uploading {}: {}".format(emoji_name, response_json))
        return response_json['ok']

    def upload_emojis(self, upload_dir, announce=True, wait_s=5):
        """Uploads any .jpg .png .gif files in a given directory,
            Announces uploads to channel, if announce=True

        Methods
             - Scan in files from directory
             - clean emoji name from file path
             - build dict: key = emoji name, value = filepath
        """
        existing_emojis = [k for k, v in self.get_emojis().items()]

        emoji_dict = {}
        for file in os.listdir(upload_dir):
            file_split = os.path.splitext(file)
            if file_split[1] in ['.png', '.jpg', '.gif']:
                filepath = os.path.join(upload_dir, file)
                emoji_name = file_split[0]
                if emoji_name not in existing_emojis:
                    emoji_dict[emoji_name] = filepath

        successfully_uploaded = []
        for k, v in emoji_dict.items():
            if k in successfully_uploaded:
                continue
            successful = self._upload_emoji(v)
            if successful:
                successfully_uploaded.append(k)
            # Wait
            print(':{}: successful - {:.2%} done'.format(k, len(successfully_uploaded) / len(emoji_dict)))
            time.sleep(wait_s)

        if announce:
            # Report the emojis captured to the channel
            # 30 emojis per line, 5 lines per post
            out_str = '\n'
            cnt = 0
            for item in successfully_uploaded:
                out_str += ':{}:'.format(item)
                cnt += 1
                if cnt % 30 == 0:
                    out_str += '\n'
                if cnt == 150:
                    self.send_message('emoji_suggestions', out_str)
                    out_str = '\n'
                    cnt = 0
            if cnt > 0:
                self.send_message('emoji_suggestions', out_str)
            return out_str
        return None

    def download_emojis(self, emoji_dict, download_dir):
        """Downloads a dict of emojis
        NOTE: key = emoji name, value = url or data
        """
        for k, v in emoji_dict.items():
            if v[:4] == 'data':
                data = v
            elif v[:4] == 'http':
                r = requests.get(v)
                data = r.content
            else:
                continue
            # Write pic to file
            fname = '{}{}'.format(k, os.path.splitext(v)[1])
            fpath = os.path.join(download_dir, fname)
            write = 'wb' if isinstance(data, bytes) else 'w'
            with open(fpath, write) as f:
                f.write(data)

    def _exact_match_emojis(self, emoji_dict, exact_match_list):
        """Matches emojis exactly"""
        matches = {}
        for k, v in emoji_dict.items():
            if k in exact_match_list:
                matches[k] = v
        return matches

    def _fuzzy_match_emojis(self, emoji_dict, fuzzy_match):
        """Fuzzy matches emojis"""
        matches = {}
        pattern = re.compile(fuzzy_match, re.IGNORECASE)
        for k, v in emoji_dict.items():
            if pattern.match(k) is not None:
                matches[k] = v
        return matches

    def match_emojis(self, exact_match_list=None, fuzzy_match=None):
        """Matches emojis in a workspace either by passing in an exact list or fuzzy-match (regex) list"""
        emoji_dict = self.get_emojis()

        matches = {}
        # Exact matches
        if exact_match_list is not None:
            exact_matches = self._exact_match_emojis(emoji_dict, exact_match_list)
            matches.update(exact_matches)
        # Fuzzy matches
        if fuzzy_match is not None:
            fuzzy_matches = self._fuzzy_match_emojis(emoji_dict, fuzzy_match)
            matches.update(fuzzy_matches)
        return matches

    def get_emojis(self):
        """Returns a dict of emojis for a given workspace"""
        resp = self.bot.api_call('emoji.list')
        if resp['ok']:
            return resp['emoji']
        else:
            print('Emoji query failed.')
            return {}

    def send_message(self, channel, message):
        """Sends a message to the specific channel"""
        self.bot.api_call(
            'chat.postMessage',
            channel=channel,
            text=message
        )

    def delete_message(self, message_dict):
        """Deletes a given message
        NOTE: Since messages are deleted by channel id and timestamp, it's recommended to
            use search_messages_by_date() to determine the messages to delete
        """
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
            resp = self.bot.api_call(
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

    def _build_emoji_letter_dict(self):
        """Sets up use of replacing words with slack emojis"""
        a2z = string.ascii_lowercase
        letter_grp = [
            'regional_indicator_',
            'letter-',
            'scrabble-'
        ]

        grp = [['{}{}'.format(y, x) for x in a2z] for y in letter_grp]

        letter_dict = {}

        for i, ltr in enumerate(list(a2z)):
            ltr_list = []
            for g in grp:
                ltr_list.append(g[i])

            letter_dict[ltr] = ltr_list

        # Additional, irregular entries
        addl = {
            'a': ['amazon', 'a', 'slayer_a', 'a_'],
            'b': ['b'],
            'e': ['slayer_e'],
            'l': ['slayer_l'],
            'm': ['m'],
            'o': ['o'],
            'r': ['slayer_r'],
            's': ['s', 'slayer_s'],
            'x': ['x'],
            'y': ['slayer_y'],
            'z': ['zabbix'],
            '.': ['dotdotdot-intensifies', 'period'],
            '!': ['exclamation', 'heavy_heart_exclamation_mark_ornament', 'grey_exclamation'],
            '?': ['question', 'grey_question', 'questionman', 'question_block'],
            '"': ['airquotes-start', 'airquotes-end'],
            "'": ['airquotes-start', 'airquotes-end'],
        }

        for k, v in addl.items():
            if k in letter_dict.keys():
                letter_dict[k] = letter_dict[k] + v
            else:
                letter_dict[k] = v
        return letter_dict

    def build_phrase(self, phrase):
        """Build your awesome phrase"""

        letter_dict = self._build_emoji_letter_dict()
        built_phrase = []
        for l in list(phrase):
            # Lookup letter
            if l in letter_dict.keys():
                vals = letter_dict[l]
                rand_l = vals[randint(0, len(vals) - 1)]
                built_phrase.append(':{}:'.format(rand_l))
            elif l == ' ':
                built_phrase.append(':blank:')
            else:
                built_phrase.append(l)

        done_phrase = ''.join(built_phrase)
        return done_phrase


