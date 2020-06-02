import random
import time

import pytesseract

from coords import *


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
        if back.visible_in(TOP_WINDOW):
            adb.tap(back[1])
        else:
            break
    try:
        wait(castle, area=BOT_WINDOW, timeout=5)
    except TimeoutError:
        adb.tap(kingdom[1])
        wait(castle, area=BOT_WINDOW, timeout=60)
        log('go_kingdom complete')


def go_kingdom_direct():
    adb.tap(kingdom[1])
    wait(castle, area=BOT_WINDOW, timeout=60)
    log('Go kingdom directly')


def go_castle():
    for _ in range(5):  # try 5 times then abort
        if back.visible():
            adb.tap(back[1])
        else:
            break
    try:
        wait(kingdom, area=BOT_WINDOW, timeout=5)
    except TimeoutError:
        adb.tap(castle[1])
        wait(kingdom, area=BOT_WINDOW, timeout=60)
        log('go_castle complete')


def ally_need_help():
    return ally_help.visible_in(BOT_WINDOW)


def help_ally():
    adb.tap(ally_help[1])


def img2str(im, config):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    return pytesseract.image_to_string(im, config=config)


def tribute_countdown():
    msg_box = (235, 555, 305, 580)
    try:
        img = adb.screenshot().crop(msg_box)
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
    jump_islands = [(460, 200), (488, 445), (525, 505)]

    go_kingdom()
    go_castle()
    for island in jump_islands:
        adb.tap(island)
    adb.tap(tribute)
    adb.tap(msg_confirm)
    time.sleep(3)
    countdown = tribute_countdown()
    if countdown is None:
        countdown = tribute_countdown()  # try one more time
    adb.tap(empty_space)
    go_kingdom_direct()
    return countdown


def get_troop_status(troop_slot):
    troop_info_area = [(8, 143, 30, 165),
                       (8, 183, 30, 205),
                       (8, 223, 30, 245),
                       (8, 263, 30, 285)]
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
    for i in range(troop_slot):
        haystack = adb.screenshot().crop(troop_info_area[i])
        for status, img in ts_images.items():
            try:
                im = PIL.Image.open(img_path(img))
                if pyautogui.locate(im, haystack, confidence=IMG_MATCH_CONFIDENCE):
                    result.append(status)
                    break
            except IOError:
                log('File is missing:', img_path(img))
    return result


def gather_super_mine(mode='ordinary'):
    adb.tap(alliance)
    adb.tap(territory)
    adb.tap(super_mine)

    coordinate_locations = [(63, 460, 210, 477),  # farm
                            (330, 460, 487, 477),  # sawmill
                            (63, 710, 210, 727),  # iron mine
                            (330, 710, 487, 727)]  # silver mine
    screenshot = adb.screenshot()
    for loc in coordinate_locations:
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

    adb.tap(screen_center)
    time.sleep(3)

    if gather.visible_in(MID_WINDOW):
        adb.tap(gather[1])
        time.sleep(3)
    else:
        log('Troop in super mine already')
        return False

    if train.visible_in(MID_WINDOW):
        adb.tap(back[1])
        log('No troops for gathering')
    else:
        if mode == 'half':
            adb.tap(half_troop)
        elif mode == 'ordinary':
            adb.tap(slot_preferred)
            adb.tap(ordinary_slot)
        adb.tap(march)
        wait(castle)
        log('Go gathering super mine complete')
    return True


def go_gathering(res, mode='ordinary'):
    res_coord = {'food': farm, 'wood': sawmill, 'iron': iron_mine, 'silver': silver_mine}
    go_kingdom()
    adb.tap(magnifier)
    time.sleep(3)
    adb.tap(res_coord[res])
    adb.tap(search)
    time.sleep(5)
    adb.tap(screen_center)
    time.sleep(3)
    adb.tap(gather[1])
    time.sleep(3)
    if train.visible_in(MID_WINDOW):
        adb.tap(back[1])
        log('No troops for gathering')
    else:
        if mode == 'half':
            adb.tap(half_troop)
        elif mode == 'ordinary':
            adb.tap(slot_preferred)
            adb.tap(ordinary_slot)
        adb.tap(march)
        wait(castle)
        log('Troops go gathering {}'.format(res))


def collect_resource():
    jump_islands = [(360, 720), (250, 642), (288, 653), (11, 387), (160, 138),
                    (40, 439), (78, 306), (77, 335), (190, 751), (65, 311),
                    (303, 186), (453, 142),
                    ]
    go_kingdom()
    go_castle()
    for island in jump_islands:
        adb.tap(island)
    go_kingdom_direct()


def repair_wall():
    jump_islands = [(360, 720), (475, 530), (533, 590), (270, 450), (80, 912),
                    ]
    go_kingdom()
    go_castle()
    for island in jump_islands:
        adb.tap(island)
    adb.tap(back[1])
    go_kingdom_direct()


def keep_activate():
    adb.swipe([random.choice(['up', 'down', 'left', 'right'])])
