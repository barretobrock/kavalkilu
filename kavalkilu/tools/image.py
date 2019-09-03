#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class IMGSlice:
    """Tools for slicing up an image"""

    def __init__(self):
        self.img_slice = __import__('image_slicer')

    def slice_img(self, img_path, squares=100):
        """Slices the image into x squares"""
        imgs = self.img_slice.slice(img_path, squares)
        return imgs

    def arrange_imgs(self, imgs):
        # Arrange the sliced images in order and prep for display
        out_str = ''
        prev_lvl = ''
        stage_emojis = {}
        for i in imgs:
            name = i.basename
            fpath = i.filename
            stage_emojis[name] = fpath
            n_split = name.split('_')
            cur_lvl = n_split[1]
            if cur_lvl != prev_lvl:
                out_str += '\n'
                prev_lvl = n_split[1]

            out_str += ':{}:'.format(name)
        return out_str


class IMG:
    """Tools for image manipulation"""
    def __init__(self):
        self.pil = __import__('PIL', fromlist=['Image'])
        self.Image = self.pil.Image

    def make_transparent(self, path):
        """Makes an image (or frame) transparent by eliminating the white background"""
        im = self.Image.open(path)
        alpha = im.getchannel('A')

        # Convert the image into P mode but only use 255 colors in the palette out of 256
        im = im.convert('RGB').convert('P', palette=self.Image.ADAPTIVE, colors=255)

        # Set all pixel values below 128 to 255 , and the rest to 0
        mask = self.Image.eval(alpha, lambda a: 255 if a <= 128 else 0)

        # Paste the color of index 255 and use alpha as a mask
        im.paste(255, mask)

        # The transparency index is 255
        im.info['transparency'] = 255

        return im









