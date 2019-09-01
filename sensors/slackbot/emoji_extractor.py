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


okrtoken = 'xoxs-715346323429-717187482855-718146882215-b8f6a4f62840dcc1f613811c38f67900b964c8d56608c28b1a87060bcf924a5e'

# For uploading
team_name = 'orbitalkettlerelay'
cookie = 'b=.2mjtb2a6kx2es3no90xjlutgh; _gcl_au=1.1.435971241.1561731335; _ga=GA1.2.1881585486.1561731335; __qca=P0-1377460889-1562356942679; optimizelyEndUserId=oeu1564422471236r0.8809903213978905; utm=%7B%22utm_source%22%3A%22in-prod%22%2C%22utm_medium%22%3A%22inprod-customize_link-slack_me%22%7D; _gid=GA1.2.1564284536.1566330414; x=2mjtb2a6kx2es3no90xjlutgh.1566476978; d=ic%2BrDosJBhmWTCMgC7VErj1pGdgkMUjFUDlkQlZ0YTh5L1hmVldhV0YvTkI4UHV2QlpVUGw3Ry8wTXptME56SEZoU2dteUh5cEJjN09ac1NRaCtSNmxCMDVaMGhOUUlVMWZnY3Zzd0ZLK0RIMmFNNjU4T1RvUENpU256OUIvQXhhd3RCM3lpTEdmcTBHNnhPVElrVElEbDlIRytqSWRITVZUeUlCLzE5WXc9PdGm62OCrX%2Bxoz%2Bec2gwcO8%3D; d-s=1566477780; lc=1566477780'


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