import time

class RoutingTableEntry:
    def __init__(self, dst_id, next_hop, metric):
        self.dst_id = dst_id
        self.next_hop = next_hop
        self.metric = metric
        self.timeout = None
        self.garbage_flag = False
        
    def init_timeout(self):
        self.timeout = time.time()

