from socket import *
import select

BUFSIZE = 4096

class Router:
    def __init__(self, router_id, inputs, outputs, timer_value):
        self.id = router_id
        self.inputs = inputs
        self.outputs = outputs
        self.timer_value = timer_value

        self.sockets = self.setup_sockets()

    def setup_sockets(self):
        sockets = {}
        for port in self.inputs:
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(('127.0.0.1', port))
            sockets[port] = s
        return sockets


    def main(self):

        print('main is running')
        while list(self.sockets.values()):
            print('in the loop!')
            readable, writable, exceptional = select.select(list(self.sockets.values()), [], [], 0)

            for s in readable:
                
                data, address = s.recvfrom(BUFSIZE)

            print("Hello world")
