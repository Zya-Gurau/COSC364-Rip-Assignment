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

        packet[cur_index] = entry.metric >> 24
        packet[cur_index+1] = 0xff & (entry.metric >> 16)
        packet[cur_index+2] = 0xffff & (entry.metric >> 8)
        packet[cur_index+3] = 0xffffff & entry.metric

        cur_index += 4
    return packet

def decode_packet(packet):
    cur_index = 4
    table_entries = []
    src_id = 0

    #check header
    if packet[0] != 2:
        raise Exception("ERROR - This protocol only implements response messages!")
    if packet[1] != 2:
        raise Exception("ERROR - Version must be 2!")
    
    src_id = packet[2] << 8 | packet[3]

    if src_id < 1 | src_id > 64000:
        raise ValueError("ERROR - router id's must be between 1 and 64000!")
    
    #check entries
    for i in range(len(packet[4:])/20):
        dst_id = packet[8] << 24 | packet[9] << 16 | packet[10] << 8 | packet[11]
        metric = packet[20] << 24 | packet[21] << 16 | packet[22] << 8 | packet[23]
        table_entries.append((dst_id, metric))
        cur_index += 20
    
    return (src_id, table_entries)



    

        
