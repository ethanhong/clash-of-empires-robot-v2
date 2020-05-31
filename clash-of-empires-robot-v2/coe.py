import adb

# constants
DEFAULT_TRIBUTE_COLLECT_INTERVAL = 600


class COE:

    def __init__(self, title, config: dict):
        self.title = title
        self.port = config['adb_port']
        self.troop_slot = config['troop_slot']
        self.wall_repair = config['wall_repair']
        self.super_mine_gathering = config['super_mine_gathering']
        self.resource_type = config['resource_type']
        self.resource_collect_time = 0
        self.tribute_collect_time = 0
        self.wall_repair_time = 0
        self.tribute_collect_interval = DEFAULT_TRIBUTE_COLLECT_INTERVAL

    def connect(self):
        return adb.connect(self.port)

    def disconnect(self):
        adb.disconnect(self.port)
