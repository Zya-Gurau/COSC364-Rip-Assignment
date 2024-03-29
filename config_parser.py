"""
    CONFIG_PARSER.PY

    This file reads through the information
    provided in a configuration file to
    create an instance of a Router.
"""
import sys
import configparser
from server import Router

DEFAULT_TIME = 30

class OutputInfo:
    """
        The output info object is used to validity
        check each section of a given outgoing
        connection, and store each of its attributes.
    """
    
    def __init__(self, output_info):
        # Split up the output information given, and perform
        # validity checks on each part.
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
    """
        Gets the Router ID value given in the
        configuration file, and runs validity
        checks.
    """
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
    """
        Gets the list of Input ports given in the
        configuration file, and runs validity
        checks.
    """
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
    """
        Gets the list of outgoing connections given
        in the configuration file, and runs
        validity checks.
    """
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
    """
        Gets the regularity with which periodic
        update messages should be sent to neighbouring
        routers, if specified, and runs validity
        checks.
    """
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
    """
        Reads the file given in the terminal - meant
        to be a configuration file for a router.
    """
    try:
        config = configparser.ConfigParser()
        config.read(filename)
    except:
        print("ERROR - File provided is not a valid configuration file!")
        exit()

    # Check that all the required fields are in the configuration file.
    options_list = ['router-id', 'input-ports', 'outputs']
    try:
        if not 'Options' in config:
            raise Exception("ERROR - There must be an Options header in configuration file!")
        for option in options_list:
            if not option in config['Options']:
                raise Exception(f"ERROR - there must be {option} value in configuration file!")
    except Exception as err:
        print(err)
        exit()

    # Read the setup info given in the configuration file.
    router_id = get_router_id(config)
    inputs = get_inputs(config)
    outputs = get_outputs(config)

    # Checks that the router is not "its own neighbour"
    try:
        inputs_set = set(inputs)
        outputs_set = set()
        for output in outputs:
            outputs_set.add(output.peer_port_no)
        intersect = inputs_set.intersection(outputs_set)
        if len(intersect) != 0:
            raise Exception("ERROR - Ports cannot simultaneously be used for both input and output!")
        if len(inputs_set) != len(outputs_set):
            raise Exception("ERROR - Routers must have the same number of input and output ports!")
    except Exception as err:
        print(err)
        exit()
    
    periodic_update = get_periodic_update(config)

    # Creates and starts a router with the relevant specifications.
    my_router = Router(router_id, inputs, outputs, periodic_update)
    print(f"Router {router_id} Started")
    my_router.main()

# Read the file named in the terminal.
read_config(sys.argv[1])

