import adb


class Device(object):

    def __init__(self, title, config: dict):
        self.title = title
        self.serial_no = config['serial_no']
        self.size = ''
        self.troop_slot = config['troop_slot']
        self.wall_repair = config['wall_repair']
        self.super_mine_gathering = config['super_mine_gathering']
        self.resource_type = config['resource_type']
        self.resource_collect_time = 0
        self.tribute_collect_time = 0
        self.wall_repair_time = 0
        self.default_tribute_collect_interval = config['default_tribute_collect_interval']
        self.tribute_collect_interval = self.default_tribute_collect_interval

    def connect(self):
        return adb.connect(self.port)

    def disconnect(self):
        adb.disconnect(self.port)
