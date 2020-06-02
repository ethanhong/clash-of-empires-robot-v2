import os

import PIL
import pyautogui

import adb

# constants
GAME_WINDOW = (0, 0, 540, 1000)
TOP_WINDOW = (0, 0, 540, 333)
MID_WINDOW = (0, 333, 540, 666)
BOT_WINDOW = (0, 666, 540, 1000)
IMG_MATCH_CONFIDENCE = 0.8


def img_path(filename):
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, 'image', filename)


class Icon(object):

    def __init__(self, img, position):
        self.img = img
        self.position = position

    def __getitem__(self, key):
        if key == 0:
            return self.img
        elif key == 1:
            return self.position

    def __repr__(self):
        return str([self.img, self.position])

    def visible(self):
        filename = img_path(self.img)
        im = PIL.Image.open(filename)
        haystack = adb.screenshot()
        return pyautogui.locate(im, haystack, confidence=IMG_MATCH_CONFIDENCE)

    def visible_in(self, area):
        filename = img_path(self.img)
        im = PIL.Image.open(filename)
        haystack = adb.screenshot().crop(area)
        return pyautogui.locate(im, haystack, confidence=IMG_MATCH_CONFIDENCE)


# icons
back = Icon('back.png', (30, 35))
castle = Icon('castle.png', (65, 890))
kingdom = Icon('kingdom.png', (65, 890))
ally_help = Icon('ally_help.png', (422, 783))
gather = Icon('gather.png', (400, 480))
train = Icon('train.png', (360, 460))

# coordinates
screen_center = (270, 480)
tribute = (220, 388)
msg_confirm = (270, 520)
empty_space = (380, 50)
alliance = (480, 915)
territory = (85, 505)
super_mine = (330, 120)
half_troop = (270, 912)
slot_preferred = (80, 912)
ordinary_slot = (380, 525)
march = (455, 910)
magnifier = (40, 698)
search = (270, 910)
farm = (230, 710)
sawmill = (316, 710)
iron_mine = (405, 710)
silver_mine = (489, 710)
