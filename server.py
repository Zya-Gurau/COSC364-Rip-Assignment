from socket import *
import select
from timer import Timer
from packets import*
from forwarding_table import *

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

        #dst_id: entry
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
    
    def resolve_update(self, data):

        src_id , table_entries = decode_packet(data)

        for entry in table_entries:

            # Add cost of link
            for output in self.outputs:
                if output.peer_id == src_id:
                    link_cost = output.link_cost
            entry.metric = min(entry.metric + link_cost, 16)
            
            #not already in table
            if entry.dst_id not in self.routing_table.keys():
                entry.next_hop = src_id
                entry.changed_flag = True
                entry.init_timeout()
                self.routing_table[entry.dst_id] = entry

            #already in table
            else:
                #from same router
                if self.routing_table[entry.dst_id].next_hop == src_id:
                    entry.changed_flag = True
                    entry.init_timeout()
                    if entry.metric == 16 and self.routing_table[entry.dst_id] != 16:
                        entry.garbage_flag = True
                        entry.init_timeout()
                    self.routing_table[entry.dst_id] = entry
                



    def check_timeout():
        pass

    def check_garbage():
        pass

    def delete_entry():
        pass

    def periodic_update(self):
        #IMPLEMENT SPLIT HORIZON AND POISONED REVERSE!!!!!!!

        for output in self.outputs:
            table_entries = [RoutingTableEntry(self.id, self.id, 0)]

            table_entries.extend(list(self.routing_table))

            packet = encode_packet(self.id, table_entries)

            list(self.sockets.values())[0].sendto(packet, ('127.0.0.1', output.peer_port_no))


    def main(self):

        self.timer = Timer(self.timer_value,  self.periodic_update)
        self.timer.start_timer()
        #self.timer.force_callback()

        
        while list(self.sockets.values()):

            readable, writable, exceptional = select.select(list(self.sockets.values()), [], [], BLOCKING_TIME)

            for s in readable:
                print(readable)
                data, address = s.recvfrom(BUFSIZE)

                if data:
                    #DEBUG
                    print("| Destination | Next Hop | Metric | Changed | Garbage |")
                    src_id , table_entries = decode_packet(data)
                    for entry in table_entries:
                        print(entry)

            self.timer.update_timer()

            
