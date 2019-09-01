import os
import requests
import time
from image_slicer import slice


img_dir = os.path.abspath('/home/bobrock/Downloads')
img_path = os.path.join(img_dir, 'big-ayy-lmao.png')

resp = slice(img_path, 100)

# Make a list of the things
out_str = ''
cur_lvl = ''
prev_lvl = ''
stage_emojis = {}
for i in resp:
    name = i.basename
    fpath = i.filename
    stage_emojis[name] = fpath
    n_split = name.split('_')
    cur_lvl = n_split[1]
    if cur_lvl != prev_lvl:
        out_str += '\n'
        prev_lvl = n_split[1]

    out_str += ':{}:'.format(name)

print(out_str)


okrtoken = ''

# For uploading
team_name = ''
cookie = ''


def _session():
    URL_CUSTOMIZE = "https://{team_name}.slack.com/customize/emoji"
    URL_ADD = "https://{team_name}.slack.com/api/emoji.add"
    URL_LIST = "https://{team_name}.slack.com/api/emoji.adminList"
    assert cookie, "Cookie required"
    assert team_name, "Team name required"
    session = requests.session()
    session.headers = {'Cookie': cookie}
    session.url_customize = URL_CUSTOMIZE.format(team_name=team_name)
    session.url_add = URL_ADD.format(team_name=team_name)
    session.url_list = URL_LIST.format(team_name=team_name)
    session.api_token = okrtoken
    return session


def upload_emoji(session, emoji_name, filename):
    data = {
        'mode': 'data',
        'name': emoji_name,
        'token': session.api_token
    }
    files = {'image': open(filename, 'rb')}
    r = session.post(session.url_add, data=data, files=files, allow_redirects=False)
    r.raise_for_status()

    # Slack returns 200 OK even if upload fails, so check for status.
    response_json = r.json()
    if not response_json['ok']:
        print("Error with uploading {}: {}".format(emoji_name, response_json))
    return response_json['ok']


# Upload process here
session = _session()
successfully_uploaded = []
for k, v in stage_emojis.items():
    if k in successfully_uploaded or 'alias' in v:
        continue
    fname = '{}{}'.format(k, os.path.splitext(v)[1])
    fpath = os.path.join(img_dir, fname)
    successful = upload_emoji(session, k, fpath)
    if successful:
        # pop out of dict
        successfully_uploaded.append(k)
    # Wait
    print(':{}: successful - {:.2%} done'.format(k, len(successfully_uploaded) / len(stage_emojis)))
    time.sleep(5)