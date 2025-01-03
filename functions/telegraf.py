import toml, logging
from functions_core.utils import *

def setup_telegraf(**args):

    logging.debug(f"Starting setup_telegraf")

    # Define the path to the telegraf.conf file
    config_file_path = '/collector/telegraf/telegraf.conf'

    # Define the variable 'poll' with your desired interval value
    poll = f"{args['poll']*60}s"

    # Read the content of the configuration file
    with open(config_file_path, 'r') as file:
        config_content = toml.load(file)

    # Check if the 'inputs' section exists, if not, create it
    if 'outputs' not in config_content:
        config_content['outputs'] = {}

    # Check if the 'cpu' section exists within 'inputs', if not, create it as an empty list
    if 'influxdb_v2' not in config_content['outputs']:
        config_content['outputs']['influxdb_v2'] = []

    if 'outputs' in config_content and 'influxdb_v2' in config_content['outputs']:
        # Loop through each entry in the 'cpu' array
        for parms_influxdb_v2 in config_content['outputs']['influxdb_v2']:
            parms_influxdb_v2['token'] = args['repository_api_key']

    # Write the updated content back to the configuration file
    with open(config_file_path, 'w') as file:
        toml.dump(config_content, file)

    logging.debug("Finished setup_telegraf")

def telegraf_local_cpu(**args):
    setup_telegraf(**args)
    logging.debug("Starting telegraf_local_cpu")

    # Define the path to the telegraf.conf file
    config_file_path = '/collector/telegraf/telegraf.conf'
    poll = f"{args['poll']*60}s"

    # Read the content of the configuration file
    with open(config_file_path, 'r') as file:
        config_content = toml.load(file)

    # Define the new cpu configuration
    cpu_config = {
        'interval': poll
    }

    # Directly set the 'cpu' section under 'inputs'
    config_content['inputs'] = {'cpu': [cpu_config]}

    # Write the updated content back to the configuration file
    with open(config_file_path, 'w') as file:
        toml.dump(config_content, file)

    logging.debug("Finished telegraf_local_cpu")


def telegraf_vmware(**args):
    logging.debug("Starting telegraf_vmware")
    setup_telegraf(**args)
    
    # Define the path to the telegraf.conf file
    config_file_path = '/collector/telegraf/telegraf.conf'
    
    new_realtime_instance = {
    'interval': [f"{args['poll']*60}s"],
    'vcenters': [args['vcenter']],
    'username': [args['user']],
    'password': [args['password']],
    'insecure_skip_verify': True,
    'force_discover_on_init': True,
    'vm_metric_exclude': ['*'],
    'datastore_metric_exclude': ['*'],
    'datacenter_metric_exclude': ['*'],
    'host_metric_exclude': ['*'],
    'cluster_metric_exclude': ['*'],
    'vsan_metric_include': ['summary.*'],
    'vsan_metric_exclude': [],
    'vsan_metric_skip_verify': False,
    'collect_concurrency': 5,
    'discover_concurrency': 5
}

    new_historical_instance = {
    'interval': '300s',
    'vcenters': ['https://someaddress/sdk'],
    'username': 'someuser@vsphere.local',
    'password': 'secret',
    'insecure_skip_verify': True,
    'force_discover_on_init': True,
    'vm_metric_exclude': ['*'],
    'datastore_metric_exclude': ['*'],
    'datacenter_metric_exclude': ['*'],
    'host_metric_exclude': ['*'],
    'cluster_metric_exclude': ['*'],
    'vsan_metric_include': ['performance.*'],
    'vsan_metric_exclude': [],
    'vsan_metric_skip_verify': False,
    'collect_concurrency': 5,
    'discover_concurrency': 5
}
    # Load the existing TOML file
    with open('config_file_path', 'r') as file:
        config_content = toml.load(file)

    # Update the inputs.vsphere sections
    config_content['inputs']['vsphere'] = [new_realtime_instance, new_historical_instance]


    # Write the updated content back to the configuration file
    with open(config_file_path, 'w') as file:
        toml.dump(config_content, file)
        
    logging("Finished telegraf_vmware")