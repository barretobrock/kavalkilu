#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu import Paths, PBullet, Camera


p = Paths()
c = Camera()
pb = PBullet(p.pushbullet_api)

imgpath = c.capture_image(p.image_dir, vflip=True, hflip=True)
pb.send_img(imgpath, os.path.basename(imgpath), 'image/png')

