r"""adb commands

    - connect(serial_no): connect devices through serial_no
    - disconnect(serial_no): connect devices through serial_no
    - kill_server(): kill all adb connections

"""
import subprocess
import time

import PIL

# global variables
cur_serial_no = None  # this variable can be modified by other modules

# constant
DELAY_BETWEEN_SCREEN_EVENT = 1.00
SUCCESS = 0
ERROR = -1


def run(cmd, timeout=30, retry=3):
    for _ in range(retry):
        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, timeout=timeout)
            out = process.stdout
            return out
        except subprocess.TimeoutExpired:
            print('[Adb command timeout]:', cmd)
            # subprocess.run('adb disconnect {}'.format(cur_serial_no))
            # subprocess.run('adb connect {}'.format(cur_serial_no))
            continue
    else:
        raise subprocess.TimeoutExpired


def connect(serial_no):
    out = run('adb connect {}'.format(serial_no))
    if 'connected to {}'.format(serial_no) in out:
        return SUCCESS
    else:
        return ERROR


def disconnect(serial_no):
    run('adb disconnect {}'.format(serial_no))


def kill_server():
    run('adb kill-server')


def launch_coe():
    run('adb -s {} shell am start -n com.leme.coe/com.leme.coe.MainActivity'.format(cur_serial_no))


def force_stop_coe():
    run('adb -s {} shell am force-stop com.leme.coe'.format(cur_serial_no))


def screenshot():
    run('adb -s {} shell screencap -p /sdcard/screen.png'.format(cur_serial_no))
    run('adb -s {} pull /sdcard/screen.png'.format(cur_serial_no))
    run('adb -s {} shell rm /sdcard/screen.png'.format(cur_serial_no))
    return PIL.Image.open('screen.png').convert('RGB')


def screen_size(serial_no):
    out = run('adb -s {} shell wm size'.format(serial_no))
    if out == '':
        return None
    out = out.split()[-1].split('x')
    out = [int(x) for x in out]  # convert str to int
    return str(min(out)) + 'x' + str(max(out))  # output a string


def tap(coord):
    run('adb -s {} shell input tap {} {}'.format(cur_serial_no, coord[0], coord[1]))
    time.sleep(DELAY_BETWEEN_SCREEN_EVENT)


def swipe(moves, duration=3000):
    tl, tr, ll, lr = (170, 380), (370, 380), (170, 580), (370, 580)
    for move in moves:
        if move == 'up':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, ll[0], ll[1], tl[0], tl[1], duration))
        elif move == 'down':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, tl[0], tl[1], ll[0], ll[1], duration))
        elif move == 'left':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, lr[0], lr[1], ll[0], ll[1], duration))
        elif move == 'right':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, ll[0], ll[1], lr[0], lr[1], duration))
        elif move == 'top_right':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, ll[0], ll[1], tr[0], tr[1], duration))
        elif move == 'top_left':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, lr[0], lr[1], tl[0], tl[1], duration))
        elif move == 'lower_right':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, tl[0], tl[1], lr[0], lr[1], duration))
        elif move == 'lower_left':
            run('adb -s {} shell input swipe {} {} {} {} {}'.format(
                cur_serial_no, tr[0], tr[1], ll[0], ll[1], duration))
        time.sleep(DELAY_BETWEEN_SCREEN_EVENT)
