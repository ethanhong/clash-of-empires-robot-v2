import subprocess
import urllib.error
import urllib.request
from time import sleep

import yaml

from coe import COE, DEFAULT_TRIBUTE_COLLECT_INTERVAL
from core import *

# global variables
COEs = []


def countdown_timer(secs):
    print("Start", end="")
    for s in range(secs - 1, 0, -1):
        sleep(1.00)
        print("..{}".format(s), end="")
    sleep(1)
    print("..GO!")


def load_config():
    with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def initialize():
    log('Initializing ...')
    global COEs
    # load config file
    configs = load_config()

    adb.kill_server()
    for title, config in configs.items():
        if adb.connect(config['serial_no']) == adb.SUCCESS:
            COEs.append(COE(title, config))

    adb.cur_serial_no = COEs[0].port

    log('Initialization finished. There are {} COE game found.'.format(len(COEs)))
    log('Configurations for each COE game:')
    for coe in COEs:
        log(' - title: {}, troop_slot:{}, wall_repair: {}, super_mine_gathering: {}, resource_type: {}'.format(
            coe.title, coe.troop_slot, coe.wall_repair, coe.super_mine_gathering, coe.resource_type))
    log('[Playing {}]'.format(COEs[0].title))


def switch_window():
    global COEs
    COEs.append(COEs.pop(0))
    adb.cur_serial_no = COEs[0].port
    log('[Switched to {}]'.format(COEs[0].title))
    t = time.time()
    log(' - resource_collect_time: {}/1200'.
        format(round(t - COEs[0].resource_collect_time)))
    log(' - tribute_collect_time: {}/{}'.
        format(round(t - COEs[0].tribute_collect_time), COEs[0].tribute_collect_interval))


def internet_on():
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=10)
        return True
    except urllib.error.URLError:
        return False


def restart():
    log('[Restart]')
    log(' - Reconnecting adb ...')
    adb.disconnect(adb.cur_serial_no)
    adb.connect(adb.cur_serial_no)

    log(' - Stopping COE ...')
    adb.force_stop_coe()

    log(' - Checking internet status ...')
    while not internet_on():
        sleep(5)

    log(' - Launching COE ...')
    adb.launch_coe()
    wait(kingdom, timeout=300)
    time.sleep(3)
    adb.tap(empty_space)

    log('Restart successful!')


def coe_bot():
    window_switch_timestamp = 0
    while True:
        try:
            # --- ally help --- #
            if ally_need_help():
                help_ally()
                log('Help ally complete')

            # --- dispatch troops to gather --- #
            troop_status = get_troop_status(COEs[0].troop_slot)
            empty_slot = COEs[0].troop_slot - len(troop_status)
            # log('[Main Loop] troop_status = {}'.format(troop_status))

            if COEs[0].super_mine_gathering \
                    and empty_slot > 0 \
                    and gather_super_mine(mode='ordinary'):
                empty_slot -= 1

            while empty_slot > 0:
                target_resource = random.choice(COEs[0].resource_type)
                go_gathering(target_resource, mode='ordinary')
                empty_slot -= 1

            # --- collect tribute --- #
            if time.time() - COEs[0].tribute_collect_time > COEs[0].tribute_collect_interval:
                log('Go collecting tribute')
                countdown = collect_tribute()
                if countdown is None:
                    COEs[0].tribute_collect_interval = DEFAULT_TRIBUTE_COLLECT_INTERVAL
                else:
                    COEs[0].tribute_collect_interval = countdown
                COEs[0].tribute_collect_time = time.time()
                log('Tribute collect complete. Will be back in', secs2hms(COEs[0].tribute_collect_interval))

            # --- collect resources --- #
            if time.time() - COEs[0].resource_collect_time > 1200:  # every 20 minutes
                log('Go collecting resources')
                collect_resource()
                COEs[0].resource_collect_time = time.time()
                log('Resources collect complete')

            # --- repair wall --- #
            if COEs[0].wall_repair and time.time() - COEs[0].wall_repair_time > 1800:  # every 30 minutes
                log('Start repair wall')
                repair_wall()
                COEs[0].wall_repair_time = time.time()
                log('Repair wall complete')

            # --- keep activate --- #
            keep_activate()

            # --- switch window --- #
            if len(COEs) > 1 and time.time() - window_switch_timestamp > 60:  # every minute
                switch_window()
                window_switch_timestamp = time.time()

        except (TimeoutError, TypeError, subprocess.TimeoutExpired) as err:
            adb.screenshot().save('err_' + time.strftime('%m%d%H%M%S', time.localtime()) + '.png')
            log('[ ***** ERROR Caught: ', err, ' *****  ]')
            restart()
            continue

        except (KeyboardInterrupt, SystemExit):
            log('Interrupt by user')
            break


if __name__ == '__main__':
    countdown_timer(3)
    initialize()
    coe_bot()
