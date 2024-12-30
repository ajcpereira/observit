import toml, logging
from functions_core.utils import *

def telegraf_local_cpu(**args):

    logging.debug(f"Starting telegraf_local_cpu ")

    # Define the path to the telegraf.conf file
    config_file_path = '/collector/telegraf/telegraf.conf'

    # Define the variable 'poll' with your desired interval value
    poll = f"{args['poll']*60}s"

    # Read the content of the configuration file
    with open(config_file_path, 'r') as file:
        config_content = toml.load(file)

    # Update the interval value in the [agent] section
    config_content['agent']['interval'] = poll

    # Check if the [[inputs.cpu]] section exists, if not, add it 
    if 'inputs.cpu' not in config_content: config_content['inputs.cpu'] = {}

    # Write the updated content back to the configuration file
    with open(config_file_path, 'w') as file:
        toml.dump(config_content, file)

    logging.debug("Finished telegraf_local_cpu")

def telegraf_vmware(**args):
    logging.debug(f"Starting telegraf_vmware")

    # Define the path to the telegraf.conf file
    config_file_path = '/collector/telegraf/telegraf.conf'

    # Define the variable 'poll' with your desired interval value
    poll = f"{args['poll']*60}s"

    # Read the content of the configuration file
    with open(config_file_path, 'r') as file:
        config_content = toml.load(file)

    # Check if the [[inputs.vmware]] section exists, if not, add it 
    if 'inputs.vmware' not in config_content: config_content['inputs.vsphere'] = {}
    # Update the interval value in the [inputs.vmware] section
    config_content['inputs.vmware']['interval'] = poll
    config_content['inputs.vmware']['vcenters'] = args['telegraf_vcenterurl']
    config_content['inputs.vmware']['username'] = args['telegraf_vcenteruser']
    config_content['inputs.vmware']['password'] = decode_base64(args['telegraf_vcenterpwd64'])
    
    # Write the updated content back to the configuration file
    with open(config_file_path, 'w') as file:
        toml.dump(config_content, file)


    logging.debug("Finished telegraf_vmware")