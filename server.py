from socket import *
import select
from timer import Timer

BUFSIZE = 4096
BLOCKING_TIME = 0.1

class Router:
    def __init__(self, router_id, inputs, outputs, timer_value):
        self.id = router_id
        self.inputs = inputs
        self.outputs = outputs
        self.timer_value = timer_value
        self.timer = None

        self.sockets = self.setup_sockets()

    def setup_sockets(self):
        sockets = {}
        for port in self.inputs:
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(('127.0.0.1', port))
            sockets[port] = s
        return sockets

    def periodic_update(self):
        print("UPDATE!")

    def main(self):

        self.timer = Timer(self.timer_value,  self.periodic_update)
        self.timer.start_timer()
        self.timer.force_callback()
        
        while list(self.sockets.values()):
            readable, writable, exceptional = select.select(list(self.sockets.values()), [], [], BLOCKING_TIME)

            for s in readable:
                
                data, address = s.recvfrom(BUFSIZE)
            
            self.timer.update_timer()

            
