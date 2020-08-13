import os
import random
import time

import PIL
import pyautogui
import pytesseract
import yaml

import adb
import coords
import device
from icon import Icon, IMG_MATCH_CONFIDENCE


def log(*args):
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime("[%H:%M:%S]")
    message = list(args)
    message.insert(0, current_time)
    print(' '.join(str(word) for word in message))


def wait(icon: Icon, area=None, timeout=20):  # timeout counts in seconds
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        if area is None:
            if icon.visible():
                break
        elif icon.visible_in(area):
            break
    else:
        raise TimeoutError('Can not find icon: {}'.format(icon))


def hms2secs(h, m, s):
    return h * 3600 + m * 60 + s


def secs2hms(secs):
    h = secs // 3600
    m = (secs - h * 3600) // 60
    s = secs % 60
    return '{}:{}:{}'.format(h, m, s)


def go_kingdom():
    for _ in range(5):  # try 5 times then abort
        if coords.back.visible_in(coords.top_window):
            adb.tap(coords.back[0])
        else:
            break
    try:
        wait(coords.castle, area=coords.bot_window, timeout=5)
    except TimeoutError:
        adb.tap(coords.kingdom[0])
        wait(coords.castle, area=coords.bot_window, timeout=60)
        log('go_kingdom complete')


def go_kingdom_direct():
    adb.tap(coords.kingdom[0])
    wait(coords.castle, area=coords.bot_window, timeout=60)
    log('Go kingdom directly')


def go_castle():
    for _ in range(5):  # try 5 times then abort
        if coords.back.visible():
            adb.tap(coords.back[0])
        else:
            break
    try:
        wait(coords.kingdom, area=coords.bot_window, timeout=5)
    except TimeoutError:
        adb.tap(coords.castle[0])
        wait(coords.kingdom, area=coords.bot_window, timeout=60)
        log('go_castle complete')


def help_ally():
    pos = coords.ally_help.visible_in(coords.bot_window)  # check if ally needs help
    if pos is not None:
        pos = pyautogui.center(pos)
        adb.tap([pos[0], pos[1]+coords.bot_window[1]])
        log('Help ally complete')


def img2str(im, config):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    return pytesseract.image_to_string(im, config=config)


def tribute_countdown():
    try:
        img = adb.screenshot().crop(coords.tribute_countdown_box)
        # img = img.point(lambda i: i < 100 and 255)
        img = PIL.ImageOps.invert(img)
        s = img2str(img, config=r'--psm 10')
        s = s.split(':')
        second = hms2secs(int(s[0]), int(s[1]), int(s[2]))
    except (IndexError, ValueError) as e:
        log('Error occurred in get_tribute_countdown():', e)
        second = None
    return second


def collect_tribute():
    go_kingdom()
    go_castle()
    for island in coords.tribute_islands:
        adb.tap(island)
    adb.tap(coords.msg_confirm)
    time.sleep(3)
    countdown = tribute_countdown()
    if countdown is None:
        countdown = tribute_countdown()  # try one more time
    adb.tap(coords.empty_space)
    go_kingdom_direct()
    return countdown


def get_troop_status(troop_slot):
    ts_images = {'back': 'ts_back.png',
                 'enemy_atk': 'ts_enemy_atk.png',
                 'gathering': 'ts_gathering.png',
                 'monster_atk': 'ts_monster_atk.png',
                 'scouting': 'ts_scouting.png',
                 'transfer': 'ts_transfer.png',
                 'reinforce': 'ts_reinforce.png',
                 'rally': 'ts_rally.png'
                 }

    result = []
    go_kingdom()
    screenshot = adb.screenshot()
    for i in range(troop_slot):
        haystack = screenshot.crop(coords.troop_info_area[i])
        for status, img in ts_images.items():
            try:
                im = PIL.Image.open(img_path(img))
                if pyautogui.locate(im, haystack, confidence=IMG_MATCH_CONFIDENCE):
                    result.append(status)
                    break
            except IOError:
                log('File is missing:', img_path(img))
    log('get_troop_status:', result)
    return result


def gather_super_mine(mode='ordinary'):
    adb.tap(coords.alliance)
    adb.tap(coords.territory)
    adb.tap(coords.super_mine)

    screenshot = adb.screenshot()
    for loc in coords.super_mine_coord_locations:
        im = screenshot.crop(loc)
        im = PIL.ImageOps.invert(im)
        result = img2str(im, config=None)
        if 'Coordinate' in result:
            x = (loc[0] + loc[2]) // 2
            y = (loc[1] + loc[3]) // 2
            adb.tap((x, y))
            break
    else:
        log('No super mine available')
        return False

    adb.tap(coords.screen_center)
    time.sleep(3)

    if coords.gather.visible_in(coords.mid_window):
        adb.tap(coords.gather[0])
        time.sleep(3)
    else:
        log('Troop in super mine already')
        return False

    if coords.train.visible_in(coords.mid_window):
        adb.tap(coords.back[0])
        log('No troops for gathering')
    else:
        if mode == 'half':
            adb.tap(coords.half_troop)
        elif mode == 'ordinary':
            adb.tap(coords.slot_preferred)
            adb.tap(coords.ordinary_slot)
        elif mode == 'superior':
            adb.tap(coords.slot_preferred)
            adb.tap(coords.superior_slot)
        adb.tap(coords.march)
        wait(coords.castle)
        log('Go gathering super mine complete')
    return True


def go_gathering(res, mode='ordinary'):
    res_coord = {'food': coords.farm, 'wood': coords.sawmill, 'iron': coords.iron_mine, 'silver': coords.silver_mine}
    go_kingdom()
    adb.tap(coords.magnifier)
    time.sleep(3)
    adb.tap(res_coord[res])
    adb.tap(coords.res_lvl_up, 2)
    adb.tap(coords.res_lvl_dn, 2)
    adb.tap(coords.search)
    time.sleep(5)
    adb.tap(coords.screen_center)
    time.sleep(3)
    adb.tap(coords.gather[0])
    time.sleep(3)
    if coords.train.visible_in(coords.mid_window):
        adb.tap(coords.back[0])
        log('No troops for gathering')
    else:
        if mode == 'half':
            adb.tap(coords.half_troop)
        elif mode == 'ordinary':
            adb.tap(coords.slot_preferred)
            adb.tap(coords.ordinary_slot)
        adb.tap(coords.march)
        wait(coords.castle)
        log('Troops go gathering {}'.format(res))


def collect_resource():
    go_kingdom()
    go_castle()
    for island in coords.resource_islands:
        adb.tap(island)
    go_kingdom_direct()


def repair_wall():
    go_kingdom()
    go_castle()
    for island in coords.wall_repair_islands:
        adb.tap(island)
    adb.tap(coords.back[0])
    go_kingdom_direct()


def keep_activate():
    adb.swipe([random.choice(['up', 'down', 'left', 'right'])])


def img_path(filename):
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, 'image', device.screen_size, filename)


def load_coordinates(size):
    with open('coordinate.yml', 'r') as stream:
        coordinate = yaml.safe_load(stream)

    coordinate = coordinate[size]

    # areas
    coords.top_window = coordinate['top_window']
    coords.mid_window = coordinate['mid_window']
    coords.bot_window = coordinate['bot_window']
    coords.troop_info_area = coordinate['troop_info_area']
    coords.super_mine_coord_locations = coordinate['super_mine_coord_locations']
    coords.tribute_countdown_box = coordinate['tribute_countdown_box']
    # icons
    coords.back = Icon(coordinate['back'][0], img_path(coordinate['back'][1]))
    coords.castle = Icon(coordinate['castle'][0], img_path(coordinate['castle'][1]))
    coords.kingdom = Icon(coordinate['kingdom'][0], img_path(coordinate['kingdom'][1]))
    coords.ally_help = Icon(coordinate['ally_help'][0], img_path(coordinate['ally_help'][1]))
    coords.gather = Icon(coordinate['gather'][0], img_path(coordinate['gather'][1]))
    coords.train = Icon(coordinate['train'][0], img_path(coordinate['train'][1]))
    # coordinate
    coords.screen_center = coordinate['screen_center']
    coords.msg_confirm = coordinate['msg_confirm']
    coords.empty_space = coordinate['empty_space']
    coords.alliance = coordinate['alliance']
    coords.territory = coordinate['territory']
    coords.super_mine = coordinate['super_mine']
    coords.half_troop = coordinate['half_troop']
    coords.slot_preferred = coordinate['slot_preferred']
    coords.ordinary_slot = coordinate['ordinary_slot']
    coords.superior_slot = coordinate['superior_slot']
    coords.march = coordinate['march']
    coords.magnifier = coordinate['magnifier']
    coords.search = coordinate['search']
    coords.farm = coordinate['farm']
    coords.sawmill = coordinate['sawmill']
    coords.iron_mine = coordinate['iron_mine']
    coords.silver_mine = coordinate['silver_mine']
    coords.res_lvl_up = coordinate['res_lvl_up']
    coords.res_lvl_dn = coordinate['res_lvl_dn']
    # islands
    coords.resource_islands = coordinate['resource_islands']
    coords.tribute_islands = coordinate['tribute_islands']
    coords.wall_repair_islands = coordinate['wall_repair_islands']
