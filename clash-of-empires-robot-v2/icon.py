import PIL
import pyautogui

import adb

# constants
IMG_MATCH_CONFIDENCE = 0.8


class Icon(object):

    def __init__(self, position, img):
        self.img = img
        self.position = position

    def __getitem__(self, key):
        if key == 0:
            return self.position
        elif key == 1:
            return self.img

    def __repr__(self):
        return str([self.img, self.position])

    def visible(self):
        filename = self.img
        im = PIL.Image.open(filename)
        haystack = adb.screenshot()
        return pyautogui.locate(im, haystack, confidence=IMG_MATCH_CONFIDENCE)

    def visible_in(self, area):
        filename = self.img
        im = PIL.Image.open(filename)
        haystack = adb.screenshot().crop(area)
        return pyautogui.locate(im, haystack, confidence=IMG_MATCH_CONFIDENCE)
