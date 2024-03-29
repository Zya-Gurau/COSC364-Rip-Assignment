# TO DO!

# Add split horizon + poisoned reverse
# Do we wanna name config_parser something easier/more descriptive e.g. setup.py?
# Apparently RIP specs say a message can have a max of 25 RIP entries. (top of page 21, bottom of page 30)
# Triggered updates: should have a timer! Specified page 29, 3.10.1 paragraph 1.

"""
    SERVER.PY

    This file creates a Router class, responsible for running all of the
    operations of a router once we have obtained the information about
    the Router's setup from the config files.

    The Router class deals with all matters of receiving and sending
    datagrams and updating the Routing Table.
"""

from socket import *
import select

from timer import Timer
from packets import *
from forwarding_table import *

BUFSIZE = 4096
BLOCKING_TIME = 0.1
INFINITY = 16

class Router:
    
    def __init__(self, router_id, inputs, outputs, timer_value):
        # Initialise the Router setup with all the information from the Configuration File.
        self.id = router_id
        self.inputs = inputs
        self.outputs = outputs
        # THIS IS JUST HERE FOR DEBUGGING!!! REMOVE THIS LATER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #self.timer_value = timer_value
        self.timer_value = 2
        self.timeout_time = timer_value * 6
        self.garbage_time = timer_value * 4

        # The routing table is implemented as a dictionary with routing_table[dst_id] = entry.
        self.routing_table = {}

        self.timer = None

        # Initialise the sockets for receiving datagrams.
        self.sockets = self.setup_sockets()


    def setup_sockets(self):
        """
            Initialises the sockets for receiving datagrams.
        """
        # We will store the sockets in a dictionary where they are indexed by the port they are listening on.
        sockets = {}
        for port in self.inputs:
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(('127.0.0.1', port))
            sockets[port] = s
        return sockets

    
    def resolve_update(self, data):
        """
            Processes any datagrams received, including making
            updates to the Routing Table if needed.
        """
        # Extract all information from the datagram received.
        src_id , table_entries = decode_packet(data)

        # trigger_update tracks if any changes are made to the Routing Table when processing the datagram.
        trigger_update = False

        # Check if each entry in the neighbour's routing table gives new routing information.
        for entry in table_entries:
            # The Router does not need to consider information about routing to itself.
            if entry.dst_id != self.id:

                # Add the cost of the link to the neighbour's costs.
                for output in self.outputs:
                    if output.peer_id == src_id:
                        link_cost = output.link_cost
                        entry.metric = min(entry.metric + link_cost, INFINITY)
                
                # If a path leads to somewhere not already in the Routing Table, add it.
                if entry.dst_id not in self.routing_table:
                    if entry.metric != INFINITY:
                        entry.changed_flag = True
                        entry.init_timeout()
                        self.routing_table[entry.dst_id] = entry

                # Adopt a path if our best path to its destination has timed out.
                elif self.routing_table[entry.dst_id].garbage_flag is True and entry.metric < INFINITY:
                    entry.changed_flag = True
                    entry.init_timeout()
                    self.routing_table[entry.dst_id] = entry

                elif entry.metric == self.routing_table[entry.dst_id].metric:
                    
                    # Reset the timeout timer if a path is already in the Routing Table.
                    if entry.next_hop == self.routing_table[entry.dst_id].next_hop:
                        self.routing_table[entry.dst_id].init_timeout()
                        
                    # Adopt a path if it is no worse than our current best path to its destination,
                    # and our best path is over halfway to timing out.
                    elif time.time() >= self.routing_table[entry.dst_id].timeout + (self.timeout_time / 2):
                        entry.changed_flag = True
                        entry.init_timeout()
                        self.routing_table[entry.dst_id] = entry

                # Replace the path in the Routing Table if we find a shorter path, or if our current path has been extended.
                elif (self.routing_table[entry.dst_id].next_hop == src_id and entry.metric != self.routing_table[entry.dst_id].metric) or entry.metric < self.routing_table[entry.dst_id].metric:
                    entry.changed_flag = True
                    self.routing_table[entry.dst_id] = entry

                    # Prepares to discard a path if its length is now infinity (i.e. it is unreachable).
                    if entry.metric == INFINITY:
                        self.routing_table[entry.dst_id].garbage_flag = True
                        self.routing_table[entry.dst_id].init_garbage()
                        trigger_update = True
                    else:
                        self.routing_table[entry.dst_id].init_timeout()

        # Send a triggered update if a route has become invalid.
        if trigger_update:
            self.triggered_update()
                
                
    def triggered_update(self):
        #SPLIT HORIZON + POISONED REVERSE!!!!!
        """
            Sends out a triggered update to neighbours detailing all
            paths in the Routing Table that have just changed.
        """
        # Gets all the recently-changed paths from the Routing Table.
        table_entries = []
        for entry in self.routing_table.values():
                if entry.changed_flag == True:
                    table_entries.append(entry)
                    entry.changed_flag = False

        # Sends these entries to each neighbour.
        packet = encode_packet(self.id, table_entries) # I DON'T THINK THIS NEEDS TO BE IN THE LOOP BUT IF IT'S BROKEN NOW PUT IT BACK IN!!!!!!!!!!!!!
        for output in self.outputs:
            list(self.sockets.values())[0].sendto(packet, ('127.0.0.1', output.peer_port_no))


    def check_timeout(self):
        # NOT CONVINCED WE ACTUALLY NEED TO CHECK IF METRIC IS INFINITY, AS THIS WOULD BE PICKED UP IN RESOLVE_UPDATE? THOUGHTS?
        """
            Adds each path in the Routing Table that has timed out or that
            is unreachable to the garbage heap, if it is not already there.
        """
        trigger_update = False
        
        for entry in self.routing_table.values():
            if self.routing_table[entry.dst_id].garbage_flag == False:
                if time.time() >= self.routing_table[entry.dst_id].timeout + self.timeout_time or self.routing_table[entry.dst_id].metric == INFINITY:
                    self.routing_table[entry.dst_id].init_garbage()
                    self.routing_table[entry.dst_id].garbage_flag = True
                    self.routing_table[entry.dst_id].metric = INFINITY
                    self.routing_table[entry.dst_id].changed_flag = True
                    trigger_update = True

        # Tells its neighbours which paths are no longer available with a triggered update.
        if trigger_update:
            self.triggered_update()


    def check_garbage(self):
        """
            Removes each path from the Routing Table whose garbage-collection
            timer has expired.
        """
        remove_list = []

        # Get a list of routers whose garbage-collection timer has expired.
        for entry in self.routing_table.values():
            if self.routing_table[entry.dst_id].garbage_flag == True:
                if time.time() >= self.routing_table[entry.dst_id].garbage_time + self.garbage_time:
                    remove_list.append(entry.dst_id)
                    
        # Remove expired paths from the Routing Table.
        for remove_id in remove_list:
            del self.routing_table[remove_id]


    def periodic_update(self):
        #IMPLEMENT SPLIT HORIZON AND POISONED REVERSE!!!!!!!
        """
            Sends the Router's full Routing Table to each of its neighbours.
        """
        # Print the Routing Table at each periodic update.
        print(f'Router {self.id} - Routing Table Update at {time.strftime("%H:%M:%S", time.localtime())}')
        print("| Destination | Next Hop | Metric | Changed | Garbage |")
        for destination in self.routing_table.keys().sorted():
            print(self.routing_table[destination])
        print(" "+"-"*53+"\n")
        
        table_entries = [RoutingTableEntry(self.id, self.id, 0)]
        table_entries.extend(list(self.routing_table.values()))
        packet = encode_packet(self.id, table_entries) # I DON'T THINK THIS NEEDS TO BE IN THE LOOP BUT IF IT'S BROKEN NOW PUT IT BACK IN!!!!!!!!!!!!!
        for output in self.outputs:
            list(self.sockets.values())[0].sendto(packet, ('127.0.0.1', output.peer_port_no))


    def main(self):
        """
            Continuously checks the Router's listening sockets for updates,
            while monitoring the up-to-dateness of its own Routing Table.
        """
        self.timer = Timer(self.timer_value,  self.periodic_update)
        self.timer.start_timer()
        #self.timer.force_callback() # CAN THIS LINE JUST BE DELETED??? IS IT NEEDED FOR ANYTHING????

        while list(self.sockets.values()):

            # Waits until the Router receives packets, or until BLOCKING_TIME elapses.
            readable, writable, exceptional = select.select(list(self.sockets.values()), [], [], BLOCKING_TIME)

            # Processes each distance vector the Router receives from its neighbours,
            # and updates the Routing Table if necessary.
            for s in readable:
                data, address = s.recvfrom(BUFSIZE)
                if data:
                    self.resolve_update(data)

            # Check if any paths in the Routing Table have timed out or should be deleted.
            self.timer.update_timer()
            self.check_timeout()
            self.check_garbage()
