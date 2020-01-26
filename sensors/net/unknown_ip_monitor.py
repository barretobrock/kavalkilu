import os
import time
import requests
import pandas as pd
from slacktools import SlackTools
from kavalkilu import Hosts, Log, LogArgParser, Paths


logg = Log('unknown_ip', log_lvl=LogArgParser().loglvl)
try:
    # Attempt to connect to Slack, don't freak out if we have a connection Error though
    st = SlackTools(logg.log_name)
    st.log.info('Hello')
except TimeoutError:
    logg.error('Unable to connect to Slack')
    st = None
hosts = Hosts()
server_ip = hosts.get_host('homeserv')['ip']
timestamp = int(round(time.time() * 1000, 0))
url = f'http://{server_ip}/admin/api_db.php?network&_={timestamp}'

lookback_period = (pd.datetime.now() - pd.Timedelta('1 days'))
prev_unknown_data_path = os.path.join(Paths().data_dir, 'unknown_clients.csv')

ips = [x['ip'] for x in hosts.hosts]
unknown_ips = []

resp = requests.get(url)
if resp.status_code == 200:
    clients = resp.json()['network']
    for i, client in enumerate(clients):
        if client['ip'] not in ips:
            unknown_ips.append(client)
else:
    logg.error('Unable to access active clients on server.')

if len(unknown_ips) > 0:
    logg.info(f'{len(unknown_ips)} unknown clients found')
    # Convert our list of dicts to dataframe, put up on #alerts
    unknown_df = pd.DataFrame(unknown_ips)
    unknown_df = unknown_df[['ip', 'name', 'firstSeen', 'lastQuery', 'numQueries', 'hwaddr', 'interface', 'macVendor']]
    # Convert unix to human
    for col in ['firstSeen', 'lastQuery']:
        human_date = pd.to_datetime(unknown_df[col], unit='s').dt.tz_localize('UTC').dt.tz_convert('US/Central')
        human_date = human_date.apply(lambda x: x.replace(tzinfo=None))
        unknown_df[col] = human_date
    # Convert : in macAddress to -
    unknown_df['hwaddr'] = unknown_df['hwaddr'].str.replace(':', '-').str.upper()

    # Filter devices that have either shown up recently or have had recent activity
    unknown_df = unknown_df[(unknown_df['firstSeen'] >= lookback_period) | (unknown_df['lastQuery'] >= lookback_period)]
    if not unknown_df.empty:
        unknown_df = unknown_df.reset_index(drop=True)
        msg = f'{unknown_df.shape[0]} unknown client{"" if unknown_df.shape[0] == 1 else "s"} with recent activity'
        logg.info(msg)
        st.send_message('#alerts', msg)
        # Read in file of already notified connections
        for i, row in unknown_df.iterrows():
            msg = f"{i + 1}: \n```{row.to_string()} \n```"
            logg.info(msg)
            st.send_message('#alerts', msg)
        # Save the dataframe
        unknown_df.to_csv(prev_unknown_data_path, index=False)

st.log.close()
logg.close()
