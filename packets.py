"""
    PACKETS.PY

    This file contains methods for encoding a list
    of Routing Table Entries into a RIP Packet, and
    vice-versa.
"""
from forwarding_table import RoutingTableEntry

INFINITY = 16

def encode_packet(src_id, table_entries):
    """
        Encodes a list of Routing Table Entries
        into a RIP Packet.
    """
    packet = bytearray(4+(len(table_entries)*20))

    # PACKET HEADER.
    # Command Field.
    packet[0] = 2
    # RIP Version Field.
    packet[1] = 2
    # Router ID of the sending router.
    packet[2] = src_id >> 8
    packet[3] = 0xff & src_id

    cur_index = 4

    # RIP ENTRIES
    for entry in table_entries:
        # Address Family Identifier.
        packet[cur_index] = 0
        packet[cur_index+1] = 2
        # Must be Zero.
        packet[cur_index+2] = 0
        packet[cur_index+3] = 0 

        cur_index+=4

        # IPv4 Address of Destination Router (implemented in assignment as Router ID).
        packet[cur_index] = entry.dst_id >> 24
        packet[cur_index+1] = 0xff & (entry.dst_id >> 16)
        packet[cur_index+2] = 0xffff & (entry.dst_id >> 8)
        packet[cur_index+3] = 0xffffff & entry.dst_id

        cur_index += 4

        # Must be Zero.
        for i in range(8):
            packet[cur_index+i] = 0

        cur_index += 8

        # Metric / Path Cost.
        cost = entry.metric
        packet[cur_index] = cost >> 24
        packet[cur_index+1] = 0xff & (cost >> 16)
        packet[cur_index+2] = 0xffff & (cost >> 8)
        packet[cur_index+3] = 0xffffff & cost

        cur_index += 4
        
    return packet

def decode_packet(packet):
    """
        Decodes incoming RIP Packets to extract
        neighbour's routing information, and
        performs validity checks.
    """
    
    table_entries = []
    src_id = 0
    
    # Perform validity checks on Header.
    if packet[0] != 2:
        print("INVALID PACKET RECEIVED - This protocol only implements Response messages!")
        return src_id, table_entries

    if packet[1] != 2:
        print("INVALID PACKET RECEIVED - RIP Version must be 2!")
        return src_id, table_entries
    
    src_id = int(packet[2] << 8 | packet[3])

    if src_id < 1 | src_id > 64000:
        print("INVALID PACKET RECEIVED - Router IDs must be between 1 and 64000!")
        return src_id, table_entries
    
    # Perform validity checks on RTEs, ignoring
    # all invalid entries.
    cur_index = 4
    for i in range(len(packet[4:])//20):

        error_found = False
        
        # Check all the "Must be Zero" sections of the RTE are correct.
        for i in range(2,4):
            if int(packet[cur_index+i]) != 0:
                error_found = True
        for i in range(8,16):
            if int(packet[cur_index+1]) != 0:
                error_found = True
        if error_found:
            print("INVALID RTE RECEIVED.")

        afi = int(packet[cur_index] << 8 | packet[cur_index+1])
        if afi != 2:
            print("INVALID RTE RECEIVED - Address Family Identifier must be 2!")
            error_found = 2
        
        # Checks the Destination Router ID is valid.
        dst_id = int(packet[cur_index+4] << 24 | packet[cur_index+5] << 16 | packet[cur_index+6] << 8 | packet[cur_index+7])
        if dst_id < 1 | dst_id > 64000:
            print("INVALID RTE RECEIVED - Router IDs must be between 1 and 64000!")
            error_found = True

        # Checks the Path Cost is valid.
        metric = int(packet[cur_index+16] << 24 | packet[cur_index+17] << 16 | packet[cur_index+18] << 8 | packet[cur_index+19])
        if metric < 0 | metric > INFINITY:
            print(f"INVALID RTE RECEIVED - Metric value must be between 1 and {INFINITY}!")
            error_found = True

        # Adds the RTE to the summary of the neighbour's Routing Table if it is valid.
        if not error_found:
            table_entries.append(RoutingTableEntry(dst_id, src_id, metric))
            
        cur_index += 20
    
    return src_id, table_entries
