from forwarding_table import RoutingTableEntry

def encode_packet(src_id, table_entries):
    cur_index = 4

    packet = bytearray(4+(len(table_entries)*20))

    packet[0] = 2
    packet[1] = 2
    packet[2] = src_id >> 8
    packet[3] = 0xff & src_id

    for entry in table_entries:
        packet[cur_index] = 0
        packet[cur_index+1] = 0
        packet[cur_index+2] = 0
        packet[cur_index+3] = 0 

        cur_index+=4

        packet[cur_index] = entry.dst_id >> 24
        packet[cur_index+1] = 0xff & (entry.dst_id >> 16)
        packet[cur_index+2] = 0xffff & (entry.dst_id >> 8)
        packet[cur_index+3] = 0xffffff & entry.dst_id

        cur_index += 4

        packet[cur_index] = 0
        packet[cur_index+1] = 0
        packet[cur_index+2] = 0
        packet[cur_index+3] = 0

        cur_index += 4

        packet[cur_index] = 0
        packet[cur_index+1] = 0
        packet[cur_index+2] = 0
        packet[cur_index+3] = 0

        cur_index += 4
        cost = entry.metric
        packet[cur_index] = cost >> 24
        packet[cur_index+1] = 0xff & (cost >> 16)
        packet[cur_index+2] = 0xffff & (cost >> 8)
        packet[cur_index+3] = 0xffffff & cost

        cur_index += 4
    return packet

def decode_packet(packet):
    cur_index = 4
    table_entries = []
    src_id = 0 
    #check header
    if packet[0] != 2:
        print("ERROR - This protocol only implements response messages!")
        return src_id, table_entries

    if packet[1] != 2:
        print("ERROR - Version must be 2!")
        return src_id, table_entries
    
    src_id = int(packet[2] << 8 | packet[3])

    if src_id < 1 | src_id > 64000:
        print("ERROR - router id's must be between 1 and 64000!")
        return src_id, table_entries
    
    #check entries
    for i in range(len(packet[4:])//20):
        error_bool = False

        dst_id = int(packet[cur_index+4] << 24 | packet[cur_index+5] << 16 | packet[cur_index+6] << 8 | packet[cur_index+7])

        if dst_id < 1 | dst_id > 64000:
            print("ERROR - router id's must be between 1 and 64000!")
            error_bool = True
        
        metric = int(packet[cur_index+16] << 24 | packet[cur_index+17] << 16 | packet[cur_index+18] << 8 | packet[cur_index+19])

        if metric < 0 | metric > 16:
            print("ERROR - metric value must be between 1 and 16!")
            error_bool = True

        if not error_bool:
            table_entries.append(RoutingTableEntry(dst_id, src_id, metric))
        cur_index += 20
    
    return src_id, table_entries




    

        
