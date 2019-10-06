#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu.tools.path import Paths
from kavalkilu.tools.log import Log
from kavalkilu.tools.camera import Amcrest
import urllib.request as ur
import datetime
from datetime import datetime as dt
import threading
import time
import imageio


def vid_streamer(camera, path):
    camera.realtime_stream(path_file=path)


def snapshot_giferizer(camera, freq=10):
    gif_path = os.path.join(p.data_dir, 'gif_{}.gif'.format(dt.now().strftime('%Y%m%d%H%M%S')))
    snaps = []
    images = []
    for s in range(freq):
        snap_path = os.path.join(p.data_dir, 'pic_{}.png'.format(dt.now().strftime('%Y%m%d_%H%M%S')))
        # Take snapshot
        camera.snapshot(path_file=snap_path)
        images.append(imageio.imread(snap_path))
        os.remove(snap_path)
        time.sleep(1)

    # Take all the snapshots and make into gif
    imageio.mimsave(gif_path, images)


p = Paths()
logg = Log('twitkov.speedtest_plot', p.log_dir, 'personal_twitter')
logg.debug('Logging initiated')

cred_dict = p.key_dict['webcam_api']

webcam_ip = p.kamincam_ip
cam = Amcrest(webcam_ip, 80, cred_dict['user'], cred_dict['password'])

snapshot_giferizer(cam, 10)

#TODO  Extract datetiem from email
now = dt.today()
cred_dict['date'] = now.strftime('%Y-%m-%d')
cred_dict['hr'] = now.strftime('%H')
cred_dict['trange'] = '{}-{}'.format(now.strftime('%H.%M.%S'),
                                     (now - datetime.timedelta(seconds=10)).strftime('%H.%M.%S'))

vidurl = 'rtsp://{username}:{passwd}@{ipaddr}:554//mnt/sd/{date}/001/dav/{hr}/{trange}[M][0@0][0].dav'.format(**cred_dict)

# 1. Examine emails for recent (last 2 minutes) activity
#   if email detected...

# 2. Take 5-10 snapshots of pos1, 1s apart, make gif, send
# 3. wait 20 seconds, take 5 snapshots of pos3, make gif, send
# 4. move back to pos 1, take 5 snapshots, make gif, send

ur.urlopen(vidurl)



# Set path for stream
strpath = os.path.join(p.data_dir, 'vid_{}'.format(dt.now().strftime('%Y%m%d_%H%M%S')))
snap_path = os.path.join(p.data_dir, 'pic_{}.png'.format(dt.now().strftime('%Y%m%d_%H%M%S')))

# Create thread for video stream
vthread = threading.Thread(target=vid_streamer, args=(cam, strpath))
end_time = time.time() + 10
vthread.start()
while time.time() < end_time:
    time.sleep(1)

# Terminate thread
vthread.join()

cam.snapshot(path_file=snap_path)