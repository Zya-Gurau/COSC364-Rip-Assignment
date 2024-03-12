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
        self.timeout_time = timer_value * 6
        self.garbage_time = timer_value * 4

        self.routing_table = {}

        self.timer = None

        self.sockets = self.setup_sockets()

    def setup_sockets(self):
        sockets = {}
        for port in self.inputs:
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(('127.0.0.1', port))
            sockets[port] = s
        return sockets

    def check_timeout():
        pass

    def check_garbage():
        pass

    def delete_entry():
        pass

    def periodic_update(self):
        #DEBUG!!!!!
        print("UPDATE!!")
        test_string = "hello!!"

        
        list(self.sockets.values())[0].sendto(test_string.encode(), ('127.0.0.1', self.outputs[0].peer_port_no))


    def main(self):

        self.timer = Timer(self.timer_value,  self.periodic_update)
        self.timer.start_timer()
        self.timer.force_callback()

        
        while list(self.sockets.values()):

            readable, writable, exceptional = select.select(list(self.sockets.values()), [], [], BLOCKING_TIME)

            for s in readable:
                
                data, address = s.recvfrom(BUFSIZE)

                #DEBUG !!!!!
                print(data.decode())

            self.timer.update_timer()

            
