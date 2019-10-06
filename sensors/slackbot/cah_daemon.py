# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import re
import traceback
import sys
import daemonize
from random import shuffle
from kavalkilu import Keys, GSheetReader, Log


# Initiate logging
log = Log('cah_bot', log_lvl='DEBUG')
log.debug('Logging initiated.')

pid = '/tmp/cah_bot.pid'


class CAHBot:
    """Bot for playing Cards Against Humanity on Slack"""
    help_txt = """
    Hi! I'm Wizzy and I help you play shitty games!
    *Commands*:
     - `cah new game [OPTIONS]`: start a new CAH game
        optional flags:
            - `-(set|s) <card-set-name>`: choose a specific card set (standard, indeed) default: *standard*
            - `-skip <disp-name1,disp-name2>`: skip some channel members
     - `cah pick <card-index>`: pick your card for the round
     - `cah (points|score|scores)`: show points/score of all players
     - `cah status`: get the current status of the game
     - `cah toggle dm`: Toggles whether or not you receive cards as a DM from Wizzy (default is off)
     - `cah choose <card-index>`: used by the judge to determine the best card from picks
     - `cah new round`: continue gameplay to a new round
     - `cah end game`: end the current game
     - `cah refresh sheets`: Refreshes the GSheets that contain the card sets
    """

    def __init__(self):
        #self.log = Log('cah_bot')
        slack = __import__('slackclient')
        # Key starting with 'xoxb...'
        bot_token = Keys().get_key('wizzy-bot-user-token')
        self.bot = slack.SlackClient(bot_token)
        # Key starting with 'xoxp...'
        user_token = Keys().get_key('wizzy-token')
        self.user = slack.SlackClient(user_token)

        # Starting number of cards for each player
        self.DECK_SIZE = 5
        self.bot_id = self.bot.api_call('auth.test')['user_id']
        self.RTM_READ_DELAY = 1
        self.MENTION_REGEX = "^(cah)(.*)"
        # For storing game info
        self.game_dict = {
            'players': self._filter_humans(self._get_users_info(self._get_channel_members())),
        }
        self.set_dict = {}
        self._read_in_sheets()

    def run_rtm(self):
        """Initiate real-time messaging"""
        if self.bot.rtm_connect(with_team_state=False):
            print('CAH bot is running.')

            self.message_grp('Rebooted and ready to play! :hyper-tada:')
            while True:
                try:
                    msg_packet = self.parse_bot_commands(self.bot.rtm_read())
                    if msg_packet is not None:
                        self.handle_command(**msg_packet)
                    time.sleep(self.RTM_READ_DELAY)
                except Exception as e:
                    print('{} Traceback:{}'.format(e, ''.join(traceback.format_tb(e.__traceback__))))
                    self.bot.rtm_connect(with_team_state=False)
        else:
            print('Connection failed.')

    def parse_direct_mention(self, message):
        """Parses user and other text from direct mention"""
        matches = re.search(self.MENTION_REGEX, message, re.IGNORECASE)
        if matches is not None:
            user_id = matches.group(1).lower()
            message_txt = matches.group(2).lower().strip()
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
                if user_id == 'cah':
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
        if message == 'help':
            response = self.help_txt
        elif message.startswith('new game'):
            self.new_game(message)
        elif message == 'new round':
            self.new_round()
        elif message == 'end game':
            self.end_game()
        elif message.startswith('pick'):
            self.process_picks(user, message)
        elif message.startswith('choose'):
            self.choose_card(user, message)
        elif message in ['points', 'score', 'scores']:
            self.display_points()
        elif message == 'toggle dm':
            self.toggle_card_dm(user)
        elif message == 'status':
            self.display_status()
        elif message == 'refresh sheets':
            if self.game_dict['status'] not in ['ended']:
                self.message_grp('Please end the game before refreshing :))))))')
            else:
                self._read_in_sheets()
                response = 'Sheets have been refreshed! `{}`'.format(','.join(self.set_dict.keys()))
        elif message != '':
            response = "I didn't understand this: `{}`\n " \
                       "Use `cah help` to get a list of my commands.".format(message)

        if response is not None:
            resp_dict = {
                'user': user
            }
            self.send_message(channel, response.format(**resp_dict))

    def _read_in_sheets(self):
        """Reads in GSheets for Viktor"""
        gs = GSheetReader(Keys().get_key('cah_sheet'))
        sheets = gs.sheets
        self.set_dict = {}
        for sheet in sheets:
            self.set_dict.update({
                sheet.title: gs.get_sheet(sheet.title)
            })

    def send_message(self, channel, message):
        """Sends a message to the specific channel"""
        self.user.api_call(
            'chat.postMessage',
            channel=channel,
            text=message
        )

    def message_grp(self, message):
        """Wrapper to send message to whole channel"""
        self.send_message('cah', message)

    def new_game(self, message):
        """Begins a new game"""
        msg_split = message.split()
        if '-skip' in msg_split and len(msg_split) > 3:
            # We're going to skip some players
            skip_idx = msg_split.index('-skip')
            skip_players = msg_split[skip_idx + 1].split(',')
        else:
            skip_players = None

        if any([x in msg_split for x in ['-set', '-s']]) and len(msg_split) > 3:
            # We're going to skip some players
            set_idx = None
            for s in ['-set', '-s']:
                try:
                    set_idx = msg_split.index(s)
                except ValueError:
                    continue
            if set_idx is None:
                self.message_grp('Could not find the \\-[s]?et flag. Defaulting to standard set.')
                card_set = 'standard'
            else:
                card_set = msg_split[set_idx + 1].strip()
        else:
            card_set = 'standard'

        cards = self._read_in_cards(set_type=card_set)
        black_cards = cards['q']
        white_cards = cards['a']
        # Shuffle cards
        shuffle(black_cards)
        shuffle(white_cards)

        self.message_grp('New game started! Cards have been shuffled. Generating players...')
        # players = self._filter_humans(self._get_users_info(self._get_channel_members()))
        players = self.game_dict['players']

        # Skipping players
        if skip_players is not None:
            for skip_player in skip_players:
                # pop out any player that we don't want to participate
                if skip_player in [x['display_name'].lower() for x in players]:
                    # Mark them as skipped
                    player_idx = players.index([x for x in players if x['display_name'].lower() == skip_player][0])
                    players[player_idx]['skip'] = True
                    self.message_grp('Skipping: *{display_name}*'.format(**skip_player))

        shuffle(players)
        self.message_grp('Judge order: {}'.format(' -> '.join([x['display_name'] for x in players])))

        # store game details in a dict
        self.game_dict.update({
            'status': 'initiated',
            'players': players,
            'player_names': ','.join([x['display_name'] for x in players]),
            'judge': players[0],
            'remaining_white': white_cards,
            'remaining_black': black_cards,
        })

        self.new_round(replace_all=True)

    def _get_channel_members(self):
        resp = self.user.api_call(
            'conversations.members',
            channel='CMPV3K8AE'
        )
        if resp['ok']:
            return resp['members']
        return None

    def _get_users_info(self, user_list):
        user_info = []
        for user in user_list:
            resp = self.user.api_call(
                'users.info',
                user=user
            )

            if resp['ok']:
                user_info.append(resp['user'])
        return user_info

    def _filter_humans(self, user_list):
        """Filters human users from bots
        Takes in a list of user details from get_users_info
        """
        humans = []
        for user in user_list:
            if not user['is_bot']:
                user_cleaned = {
                    'id': user['id'],
                    'display_name': user['profile']['display_name'].lower(),
                    'real_name': user['real_name'],
                    'is_bot': user['is_bot'],
                    'skip': False,
                    'dm_cards': False,
                    'score': 0
                }
                humans.append(user_cleaned)
        return humans

    def _read_in_cards(self, set_type='standard'):
        """Reads in the cards"""

        if set_type in self.set_dict.keys():
            set_df = self.set_dict[set_type]
            self.message_grp('Using the `{}` set.'.format(set_type))
        else:
            self.message_grp('The card set `{}` was not found. '
                             'Possible sets: `{}`.'.format(set_type, ','.join(self.set_dict.keys())))
            return None

        cards = {}
        for part in ['questions', 'answers']:
            cards[part[0]] = set_df.loc[(~set_df[part].isnull()) & (set_df[part] != ''), part].unique().tolist()

        return cards

    def toggle_card_dm(self, user_id):
        """Toggles card dming"""
        players = self.game_dict['players']
        player_idx = players.index([x for x in players if x['id'] == user_id][0])
        self.game_dict['players'][player_idx]['dm_cards'] = not self.game_dict['players'][player_idx]['dm_cards']
        # Read in the new values
        player = self.game_dict['players'][player_idx]
        self.message_grp('Card DMing for player `{display_name}` set to `{dm_cards}`'.format(**player))

    def new_round(self, replace_all=False):
        """Starts a new round"""

        if not self.game_dict['status'] in ['end_round', 'initiated']:
            # Avoid starting a new round when one has already been started
            self.message_grp('Cannot transition to new round '
                             'due to status (`{}`)'.format(self.game_dict['status']))
            return None

        if replace_all:
            # This is done for the first round of the game
            num_cards = self.DECK_SIZE
            players = self.game_dict['players']
            judge = self._find_new_judge(new_game=True)
        else:
            # This is for sequential rounds
            num_cards = 1
            players = self.game_dict['players']
            judge = self._find_new_judge()

        self.message_grp('*{display_name}* is the judge!'.format(**judge))
        self._private_channel_message(judge['id'], 'cah', "You're the judge this round!")
        white_cards = self.game_dict['remaining_white']
        black_cards = self.game_dict['remaining_black']

        if len(black_cards) == 0:
            self.message_grp('No more black cards! Game over!')
            self.display_points()
            self.end_game()
        else:
            current_black = black_cards.pop(0)

        self.message_grp('Distributing cards...')

        # Distribute cards
        for i, player in enumerate(players):
            # Remove any possible pick from last round
            _ = player.pop('pick', None)
            if len(white_cards) > 0:
                cards = white_cards[:num_cards]
                white_cards = white_cards[num_cards:]
                if replace_all:
                    player['cards'] = cards
                else:
                    if 'prev_judge' in self.game_dict:
                        # If the player was previously a judge, don't give them another card
                        #   because they didn't play last round
                        if self.game_dict['prev_judge'] != player:
                            player['cards'] += cards
                    else:
                        player['cards'] += cards
                if player != self.game_dict['judge']:
                    # Only send these to a player during this round
                    self._distribute_cards(player)
                players[i] = player
            else:
                self.message_grp('No more cards left to deal!')
                break

        # Show group this round's question
        self.message_grp("Q: `{}`".format(current_black))
        # Load everything back into the game dict
        self.game_dict.update({
            'status': 'players_decision',
            'players': players,
            'remaining_white': white_cards,
            'remaining_black': black_cards,
            'current_black': current_black,
            'chosen_cards': []
        })

    def _find_new_judge(self, new_game=False):
        """Determines the next judge by order of players"""
        players = self.game_dict['players']
        judge = self.game_dict['judge']
        judge_pos = players.index(judge)
        if new_game:
            # In new_game(), the judge is the first player in the shuffled list of players
            return judge
        if judge_pos < len(players) - 1:
            # Increment up one player to get new judge
            new_judge_pos = judge_pos + 1
        else:
            # We're at the end of the list of players, go back to the start
            new_judge_pos = 0
        new_judge = players[new_judge_pos]
        self.game_dict['judge'] = new_judge
        self.game_dict['prev_judge'] = judge
        return new_judge

    def _private_channel_message(self, user_id, channel, message):
        """Send a message to a user on the channel"""
        resp2 = self.bot.api_call(
            'chat.postEphemeral',
            channel=channel,
            user=user_id,
            text=message
        )
        if not resp2['ok']:
            raise Exception(resp2['error'])

    def _private_message(self, user_id, message):
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

    def _distribute_cards(self, user_dict):
        """Distribute cards to user"""

        cards_msg = ['\t`{}`: {}'.format(i, x) for i, x in enumerate(user_dict['cards'])]

        msg_txt = 'Here are your cards:\n{}'.format('\n'.join(cards_msg))
        self._private_channel_message(user_dict['id'], 'cah', msg_txt)
        if user_dict['dm_cards']:
            # DM cards if user has toggled that on
            msg_txt2 = "Psst - In case you didn't get the cards in the channel, here they are. " \
                       "*Reply in #cah though.*\n\n{}".format(msg_txt)
            self._private_message(user_dict['id'], msg_txt2)

    def process_picks(self, user, message):
        """Processes the card selection made by the user"""
        if self.game_dict['status'] != 'players_decision':
            # Prevent this method from being called outside of the player's decision stage
            return None
        # Process the message
        pick = self._get_pick(user, message, pick_idx=1)
        if pick is None:
            return None
        elif pick > 4 or pick < 0:
            self.message_grp('<@{}> I think you picked outside the range of suggestions.'.format(user))
            return None
        for i, player in enumerate(self.game_dict['players']):
            if player['id'] == user and player != self.game_dict['judge']:
                if 'pick' not in player.keys():
                    player['pick'] = player['cards'].pop(pick)
                    self.message_grp("{display_name}'s pick has been registered.".format(**player))
                    # Store player's pick
                    self.game_dict['players'][i] = player
                else:
                    self.message_grp("{display_name}, you've already picked this round.".format(**player))
                break

        # See who else has yet to decide
        remaining = []
        for i, player in enumerate(self.game_dict['players']):
            if 'pick' not in player.keys() and player != self.game_dict['judge']:
                remaining.append(player['display_name'])
        if len(remaining) == 0:
            self.message_grp('All players have made their picks.')
            self.message_grp('`{}` to judge'.format(self.game_dict['judge']['display_name']))
            self.game_dict['status'] = 'judge_decision'
            self._display_picks()
        else:
            self.message_grp('{} players remaining to decide: {}'.format(len(remaining), ', '.join(remaining)))

    def _get_pick(self, user, message, pick_idx):
        """Processes a number from a message"""
        # Process the message
        msg_split = message.split()
        if len(msg_split) > 1:
            if msg_split[pick_idx].isnumeric():
                pick = int(msg_split[pick_idx])
                return pick
            else:
                self.message_grp("<@{}> - I didn't understand your pick: {}".format(user, message))
        else:
            self.message_grp("<@{}> - I didn't understand your pick: {}".format(user, message))
        return None

    def _display_picks(self):
        """Shows a random order of the picks"""
        picks = []
        for i, player in enumerate(self.game_dict['players']):
            if 'pick' in player.keys() and player != self.game_dict['judge']:
                player_details = {
                    'id': player['id'],
                    'pick': player['pick']
                }
                picks.append(player_details)
        shuffle(picks)
        pick_str = '\n'.join(['`{}`: {}'.format(x, y['pick']) for x, y in enumerate(picks)])
        self.message_grp('Q: `{}`\n\n{}'.format(self.game_dict['current_black'], pick_str))
        self.game_dict['chosen_cards'] = picks

    def choose_card(self, user, message):
        """For the judge to choose the winning card"""
        if self.game_dict['status'] != 'judge_decision':
            # Prevent this method from being called outside of the judge's decision stage
            return None

        if user == self.game_dict['judge']['id']:
            pick = self._get_pick(user, message, pick_idx=1)
            if pick > len(self.game_dict['players']) - 2 or pick < 0:
                self.message_grp('I think you picked outside the range of suggestions.')
                return None
            else:
                # Get the list of cards picked by each player
                chosen_cards = self.game_dict['chosen_cards']
                for i, player in enumerate(self.game_dict['players']):
                    if player['id'] == chosen_cards[pick]['id']:
                        player['score'] += 1
                        self.message_grp("Winning card: {}\n\t({display_name}, new score: *{score}*pts)".format(
                            chosen_cards[pick]['pick'], **player))
                        self.game_dict['status'] = 'end_round'
                        self.message_grp('Round ended. `cah new round` to start another.')
                        break
        else:
            self.message_grp("Get yo _stanky_ ass outta here, you ain't the judge")

    def end_game(self):
        """Ends the current game"""
        self.game_dict['status'] = 'ended'
        self.message_grp('The game has ended.')

    def display_points(self):
        """Displays points for all players"""
        points = ['*{display_name}*: {score}'.format(**player) for player in self.game_dict['players']]
        self.message_grp('*Current Scores*\n{}'.format('\n'.join(points)))

    def display_status(self):
        """Displays points for all players"""
        num_white = len(self.game_dict['remaining_white'])
        num_black = len(self.game_dict['remaining_black'])

        status_list = [
            '`current game status`: {status}',
            '`players`: {player_names}',
            '`judge`: {}'.format(self.game_dict['judge']['display_name']),
            '`remaining white cards`: {}'.format(num_white),
            '`remaining black cards`: {}'.format(num_black),
        ]

        status_message = '\n'.join(status_list).format(**self.game_dict)
        self.message_grp(status_message)


if __name__ == "__main__":
    cbot = CAHBot()
    daemon = daemonize.Daemonize(app='kodubot', pid=pid, action=cbot.run_rtm, logger=log, verbose=True)
    if len(sys.argv) == 2:
        cmd = sys.argv[1]
        if 'start' == cmd:
            daemon.start()
        elif 'stop' == cmd:
            cbot.message_grp('Shutting down for now! :sleepyparrot:')
            log.debug('Closing daemon')
            daemon.exit()
        else:
            print("Unknown command: {}".format(cmd))
            sys.exit(2)
        sys.exit(0)
    else:
        print("Usage: {} start|stop".format(sys.argv[0]))
        sys.exit(2)


