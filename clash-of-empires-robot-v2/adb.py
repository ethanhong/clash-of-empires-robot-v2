r"""adb commands

    - connect(port): connect devices through localhost:port
    - disconnect(port): connect devices through localhost:port
    - kill_server(): kill all adb connections

"""
import subprocess
import time

import PIL

# global variables
current_port = 0  # this variable can be modified by other modules

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
            subprocess.run('adb disconnect localhost:{}'.format(current_port))
            subprocess.run('adb connect localhost:{}'.format(current_port))
            continue
    else:
        raise subprocess.TimeoutExpired


def connect(port):
    out = run('adb connect localhost:{}'.format(port))
    if 'connected to localhost:{}'.format(port) in out:
        return SUCCESS
    else:
        return ERROR


def disconnect(port):
    run('adb disconnect localhost:{}'.format(port))


def kill_server():
    run('adb kill-server')


def launch_coe():
    run('adb -s localhost:{} shell am start -n com.leme.coe/com.leme.coe.MainActivity'.format(current_port))


def force_stop_coe():
    run('adb -s localhost:{} shell am force-stop com.leme.coe'.format(current_port))


def screenshot():
    run('adb -s localhost:{} shell screencap -p /sdcard/screen.png'.format(current_port))
    run('adb -s localhost:{} pull /sdcard/screen.png'.format(current_port))
    run('adb -s localhost:{} shell rm /sdcard/screen.png'.format(current_port))
    return PIL.Image.open('screen.png').convert('RGB')


def tap(coord):
    run('adb -s localhost:{} shell input tap {} {}'.format(current_port, coord[0], coord[1]))
    time.sleep(DELAY_BETWEEN_SCREEN_EVENT)


def swipe(moves, duration=3000):
    tl, tr, ll, lr = (170, 380), (370, 380), (170, 580), (370, 580)
    for move in moves:
        if move == 'up':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, ll[0], ll[1], tl[0], tl[1], duration))
        elif move == 'down':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, tl[0], tl[1], ll[0], ll[1], duration))
        elif move == 'left':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, lr[0], lr[1], ll[0], ll[1], duration))
        elif move == 'right':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, ll[0], ll[1], lr[0], lr[1], duration))
        elif move == 'top_right':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, ll[0], ll[1], tr[0], tr[1], duration))
        elif move == 'top_left':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, lr[0], lr[1], tl[0], tl[1], duration))
        elif move == 'lower_right':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, tl[0], tl[1], lr[0], lr[1], duration))
        elif move == 'lower_left':
            run('adb -s localhost:{} shell input swipe {} {} {} {} {}'.format(
                current_port, tr[0], tr[1], ll[0], ll[1], duration))
        time.sleep(DELAY_BETWEEN_SCREEN_EVENT)

# def connect(port):
#     p = subprocess.Popen('adb connect localhost:{}'.format(port), stdout=subprocess.PIPE)
#     out, err = p.communicate()
#     out = out.decode("utf-8")  # decode bytes to string
#     if 'connected to localhost:{}'.format(port) in out:
#         return SUCCESS
#     else:
#         return ERROR
#
#
# def disconnect(port):
#     subprocess.call('adb disconnect localhost:{}'.format(port))
#
#
# def kill_server():
#     subprocess.call('adb kill-server')
#
#
# def launch_coe():
#     subprocess.call(adb_shell() + 'am start -n com.leme.coe/com.leme.coe.MainActivity')
#
#
# def force_stop_coe():
#     subprocess.call(adb_shell() + 'am force-stop com.leme.coe')
#
#
# def screenshot():
#     subprocess.call(adb_shell() + 'screencap -p /sdcard/screen.png')
#     subprocess.call('adb -s localhost:{} pull /sdcard/screen.png'.format(current_port), stdout=subprocess.PIPE)
#     subprocess.call(adb_shell() + 'rm /sdcard/screen.png')
#     return PIL.Image.open('screen.png').convert('RGB')
#
#
# def tap(coord):
#     subprocess.call(adb_shell() + 'input tap {} {}'.format(coord[0], coord[1]))
#
#
# def swipe(moves, duration=3000):
#     tl, tr, ll, lr = (170, 380), (370, 380), (170, 580), (370, 580)
#     for move in moves:
#         if move == 'up':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 ll[0], ll[1], tl[0], tl[1], duration))
#         elif move == 'down':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 tl[0], tl[1], ll[0], ll[1], duration))
#         elif move == 'left':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 lr[0], lr[1], ll[0], ll[1], duration))
#         elif move == 'right':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 ll[0], ll[1], lr[0], lr[1], duration))
#         elif move == 'top_right':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 ll[0], ll[1], tr[0], tr[1], duration))
#         elif move == 'top_left':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 lr[0], lr[1], tl[0], tl[1], duration))
#         elif move == 'lower_right':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 tl[0], tl[1], lr[0], lr[1], duration))
#         elif move == 'lower_left':
#             subprocess.call(adb_shell() + 'input swipe {} {} {} {} {}'.format(
#                 tr[0], tr[1], ll[0], ll[1], duration))
