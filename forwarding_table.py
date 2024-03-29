import time

class RoutingTableEntry:
    def __init__(self, dst_id, next_hop, metric):
        self.dst_id = dst_id
        self.next_hop = next_hop
        self.metric = metric
        self.timeout = None
        self.garbage_time = None
        self.changed_flag = False
        self.garbage_flag = False
        
    def init_timeout(self):
        self.timeout = time.time()

    def init_garbage(self):
        self.garbage_time = time.time()

    def __repr__(self):
        return "|{:^13}|{:^10}|{:^8}|{:^9}|{:^9}|\n".format(self.dst_id, self.next_hop, 
                                                            self.metric, self.changed_flag, self.garbage_flag)

