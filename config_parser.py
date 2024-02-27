"""
"""

import configparser

class RipConfig:
    def __init__(self, router_id, inputs, outputs, periodic_update = 30):
        self.router_id = router_id
        self.inputs = inputs
        self.outputs = outputs
        self.periodic_update = periodic_update

def get_router_id(config):
    try: 
        id = int(config['Options']['router-id'])
        if id < 1 | id > 64000:
            raise ValueError
        return id
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
            raise Exception("ERROR - There must be at leat one input port!")
        
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
    periodic_update = get_periodic_update(config)

