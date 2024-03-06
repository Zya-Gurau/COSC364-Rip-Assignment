"""
"""

import configparser

DEFAULT_TIME = 30

class RipConfig:
    def __init__(self, router_id, inputs, outputs, periodic_update = 30):
        self.router_id = router_id
        self.inputs = inputs
        self.outputs = outputs
        self.periodic_update = periodic_update

class OutputInfo:
    def __init__(self, output_info):
        try:
            details = output_info.split('-')
            for i in range(len(details)):
                details[i] = int(details[i])
            self.peer_port_no = details[0]
            self.link_cost = details[1]
            self.peer_id = details[2]

            if self.peer_port_no < 1024 | self.peer_port_no > 64000:
                raise ValueError("ERROR - Peer port number must be between 1,024 and 64,000!")

            if not 1 <= self.link_cost <= 16:
                raise ValueError("ERROR - Link costs must all be between 1 and 16!")

            if not 1 <= self.peer_id <= 64000:
                raise ValueError("ERROR - Peer port id numbers must be between 1 and 64,000!")

            
        except TypeError:
            print(f"ERROR - Invalid type for output value {output_info}!")
            exit()
        except IndexError:
            print(f"ERROR - Insufficient fields for output value {output_info}!")
            exit()
        except ValueError as err:
            print(err)
            exit()
        

def get_router_id(config):
    try: 
        router_id = int(config['Options']['router-id'])
        if router_id  < 1 | router_id  > 64000:
            raise ValueError
        return router_id 
    except TypeError:
        print("ERROR - Invalid type for router-id!")
        exit()
    except ValueError:
        print("ERROR - router-id must be between 1 and 64000!")
        exit()



def get_inputs(config):
    try:
        inputs = config['Options']['input-ports'].split(',')

        if len(inputs) == 0:
            raise Exception("ERROR - There must be at least one input port!")
        
        inputs = [port.strip() for port in inputs]
        inputs = [int(port) for port in inputs]

        for port in inputs:
            if port < 1024 | port > 64000:
                raise ValueError
        
        input_set = set(inputs)
        if len(inputs) != len(input_set):
            raise Exception("ERROR - There must not be duplicate input ports!")

        return inputs

    except TypeError:
        print("ERROR - Input ports must be an integer between 1024 and 64000!")
        exit()
    except ValueError:
        print("ERROR - Input ports must be an integer between 1024 and 64000!")
        exit()
    except Exception as err:
        print(err)
        exit()

def get_outputs(config):
    try:
        outputs = config['Options']['outputs'].split(',')

        if len(outputs) == 0:
            raise Exception("ERROR - There must be at least one output port!")

        outputs = [port.strip() for port in outputs]
        outputs = [OutputInfo(output) for output in outputs]

        output_set = set()
        for output in outputs:
            output_set.add(output.peer_port_no)
        if len(output_set) != len(outputs):
            raise Exception("ERROR - Output port numbers must be unique!")

        return outputs

    except Exception as err:
        print(err)
        exit()

def get_periodic_update(config):
    try:
        if not "periodic-update" in config['Options']:
            return DEFAULT_TIME

        timer_value = int(config['Options']['periodic-update'].strip())
        if timer_value < 1:
            raise ValueError

        return timer_value

    except TypeError:
        print("ERROR - Periodic Update value must be an integer!")
        exit()
    except ValueError:
        print("ERROR - Periodic Update value must be at least 1s!")
        exit()

def read_config(filename):

    config = configparser.ConfigParser()
    config.read(filename)

    options_list = ['router-id', 'input-ports', 'outputs']

    try:
        if not 'Options' in config:
            raise Exception("ERROR - There must be an Options header in config file!")
        for option in options_list:
            if not option in config['Options']:
                raise Exception(f"ERROR - there must be {option} value in config file!")
    except Exception as err:
        print(err)
        exit()

    router_id = get_router_id(config)
    inputs = get_inputs(config)
    outputs = get_outputs(config)

    try:
        inputs_set = set(inputs)
        outputs_set = set()
        for output in outputs:
            outputs_set.add(output.peer_port_no)
        intersect = inputs_set.intersection(outputs_set)
        if len(intersect) != 0:
            raise Exception("ERROR - Ports cannot simultaneously be used for both input and output!")
    except Exception as err:
        print(err)
        exit()
    
    periodic_update = get_periodic_update(config)

    # NEEDS TO RETURN SOMETHING

read_config('config1.txt')

