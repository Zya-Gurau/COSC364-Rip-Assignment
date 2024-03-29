#todo 
#add triggered updates
#add split horizon + poisoned reverse
# fix changed flag
# random timer offset

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
        #self.timer_value = timer_value
        self.timer_value = 2
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
        trigger_update = False

        for entry in table_entries:
            if entry.dst_id != self.id:

                # Add cost of link
                for output in self.outputs:
                    if output.peer_id == src_id:
                        link_cost = output.link_cost
                        entry.metric = min(entry.metric + link_cost, 16)
                
                #not already in table
                if entry.dst_id not in self.routing_table.keys():
                    if entry.metric != 16:
                        #entry.next_hop = src_id
                        #entry.metric = new_metric
                        entry.changed_flag = True
                        entry.init_timeout()
                        self.routing_table[entry.dst_id] = entry
                        trigger_update = True

                #already in table
                
                if self.routing_table[entry.dst_id].garbage_flag == True and entry.metric < 16:
                    #entry.next_hop = src_id
                    entry.changed_flag = True
                    entry.init_timeout()
                    self.routing_table[entry.dst_id] = entry
                    trigger_update = True

                #if metrics same
                elif entry.metric == self.routing_table[entry.dst_id].metric:
                    if time.time() >= self.routing_table[entry.dst_id].timeout + (self.timeout_time //2):
                        #entry.next_hop = src_id
                        #entry.metric = new_metric
                        entry.changed_flag = True
                        entry.init_timeout()
                        self.routing_table[entry.dst_id] = entry
                    else:
                        self.routing_table[entry.dst_id].init_timeout()
                    
                #from same router
                elif self.routing_table[entry.dst_id].next_hop == src_id:
                    #entry.changed_flag = True
                    entry.init_timeout()
                elif (self.routing_table[entry.dst_id].next_hop == src_id and entry.metric != self.routing_table[entry.dst_id].metric) or entry.metric < self.routing_table[entry.dst_id].metric:
                    entry.changed_flag = True
                    self.routing_table[entry.dst_id] = entry

                    trigger_update = True

                    if entry.metric == 16 and self.routing_table[entry.dst_id] != 16:
                        self.routing_table[entry.dst_id].garbage_flag = True
                        self.routing_table[entry.dst_id].init_garbage()
                        self.routing_table[entry.dst_id].changed_flag = True
                    else:
                        self.routing_table[entry.dst_id].init_timeout()
        

        print("| Destination | Next Hop | Metric | Changed | Garbage |")
        for entry in self.routing_table.values():
            print(entry)
        
        if trigger_update:
            self.triggered_update()
                
                
    def triggered_update(self):
        #SPLIT HORIZON + POISONED REVERSE!!!!!
        table_entries = []
        for entry in self.routing_table.values():
                if entry.changed_flag == True:
                    table_entries.append(entry)
                    entry.changed_flag = False
        for output in self.outputs:
            
            packet = encode_packet(self.id, table_entries)

            list(self.sockets.values())[0].sendto(packet, ('127.0.0.1', output.peer_port_no))


    def check_timeout(self):
        for entry in self.routing_table.values():
            if self.routing_table[entry.dst_id].garbage_flag == False:
                if time.time() >= self.routing_table[entry.dst_id].timeout + self.timeout_time or self.routing_table[entry.dst_id].metric == 16:
                    self.routing_table[entry.dst_id].init_garbage()
                    self.routing_table[entry.dst_id].garbage_flag = True
                    self.routing_table[entry.dst_id].metric = 16
                    self.routing_table[entry.dst_id].changed_flag = True
                    self.triggered_update()


    def check_garbage(self):
        remove_list = []
        for entry in self.routing_table.values():
            if self.routing_table[entry.dst_id].garbage_flag == True:
                if time.time() >= self.routing_table[entry.dst_id].garbage_time + self.garbage_time:
                    remove_list.append(entry.dst_id)
        for remove_id in remove_list:
            del self.routing_table[remove_id]

    def delete_entry():
        pass

    def periodic_update(self):
        #IMPLEMENT SPLIT HORIZON AND POISONED REVERSE!!!!!!!

        for output in self.outputs:
            table_entries = [RoutingTableEntry(self.id, self.id, 0)]

            table_entries.extend(list(self.routing_table.values()))

            packet = encode_packet(self.id, table_entries)

            list(self.sockets.values())[0].sendto(packet, ('127.0.0.1', output.peer_port_no))


    def main(self):

        self.timer = Timer(self.timer_value,  self.periodic_update)
        self.timer.start_timer()
        #self.timer.force_callback()

        
        while list(self.sockets.values()):

            readable, writable, exceptional = select.select(list(self.sockets.values()), [], [], BLOCKING_TIME)

            for s in readable:
                data, address = s.recvfrom(BUFSIZE)

                if data:
                    self.resolve_update(data)

            self.timer.update_timer()
            self.check_timeout()
            self.check_garbage()



            
