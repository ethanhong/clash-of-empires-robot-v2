r"""adb commands

    - connect(port): connect devices through localhost:port
    - disconnect(port): connect devices through localhost:port
    - kill_server(): kill all adb connections

"""
import subprocess

import PIL

# global variables
current_port = 0  # this variable can be modified by other modules

# constant
SUCCESS = 0
ERROR = -1


def adb_shell():
    return 'adb -s localhost:{} shell '.format(current_port)


def connect(port):
    result = subprocess.check_output('adb connect localhost:{}'.format(port))
    result = result.decode("utf-8")  # decode bytes to string
    if 'connected to localhost:{}'.format(port) in result:
        return SUCCESS
    else:
        return ERROR


def disconnect(port):
    subprocess.check_output('adb disconnect localhost:{}'.format(port))


def kill_server():
    subprocess.check_output('adb kill-server')


def launch_coe():
    subprocess.check_output(adb_shell() + 'am start -n com.leme.coe/com.leme.coe.MainActivity')


def force_stop_coe():
    subprocess.check_output(adb_shell() + 'am force-stop com.leme.coe')


def screenshot():
    subprocess.check_output(adb_shell() + 'screencap -p /sdcard/screen.png')
    subprocess.check_output('adb -s localhost:{} pull /sdcard/screen.png'.format(current_port))
    subprocess.check_output(adb_shell() + 'rm /sdcard/screen.png')
    return PIL.Image.open('screen.png').convert('RGB')


def tap(coord):
    subprocess.check_output(adb_shell() + 'input tap {} {}'.format(coord[0], coord[1]))


def swipe(moves, duration=3000):
    tl, tr, ll, lr = (170, 380), (370, 380), (170, 580), (370, 580)
    for move in moves:
        if move == 'up':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                ll[0], ll[1], tl[0], tl[1], duration))
        elif move == 'down':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                tl[0], tl[1], ll[0], ll[1], duration))
        elif move == 'left':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                lr[0], lr[1], ll[0], ll[1], duration))
        elif move == 'right':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                ll[0], ll[1], lr[0], lr[1], duration))
        elif move == 'top_right':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                ll[0], ll[1], tr[0], tr[1], duration))
        elif move == 'top_left':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                lr[0], lr[1], tl[0], tl[1], duration))
        elif move == 'lower_right':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                tl[0], tl[1], lr[0], lr[1], duration))
        elif move == 'lower_left':
            subprocess.check_output(adb_shell() + 'input swipe {} {} {} {} {}'.format(
                tr[0], tr[1], ll[0], ll[1], duration))
