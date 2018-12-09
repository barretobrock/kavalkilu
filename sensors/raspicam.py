#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu.tools.path import Paths
from kavalkilu.tools.message import PBullet

p = Paths()
c = Camera()
pb = PBullet(p.pushbullet_api)

imgpath = c.capture_image(p.image_dir, vflip=True, hflip=True)
pb.send_img(imgpath, os.path.basename(imgpath), 'image/png')

