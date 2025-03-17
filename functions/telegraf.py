import toml, logging
from functions_core.utils import *


def setup_telegraf(**args):

    logging.debug(f"Starting setup_telegraf")

    # Define the path to the telegraf.conf file
    config_file_path = '/collector/telegraf/telegraf.conf'

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

def telegraf_vmware(**args):
    logging.debug("Starting telegraf_vmware")
    setup_telegraf(**args)  # Assuming this function is defined elsewhere in your code

    # Define the path to the telegraf.conf file
    config_file_path = '/collector/telegraf/telegraf.conf'
    poll = f"{args['poll']*60}s"  # Set polling interval in seconds

    # Manually construct the configuration for new_realtime_instance and new_historical_instance
    new_realtime_instance = { 
        'interval': poll,
        'vcenters': [str(args['telegraf_vcenterurl'])],
        'username': args['telegraf_vcenteruser'],
        'password': decode_base64(args['telegraf_vcenterpwd64']),
        'insecure_skip_verify': True,
        'datastore_metric_exclude': ['*'],
        'cluster_metric_exclude': ['*'],
        'datacenter_metric_exclude': ['*'],
        'resource_pool_metric_exclude': ['*'],
        'vsan_metric_exclude': ['*'],
        'collect_concurrency': 5,
        'discover_concurrency': 5
    }

    new_historical_instance = {
        'interval': '300s',
        'vcenters': [str(args['telegraf_vcenterurl'])],
        'username': args['telegraf_vcenteruser'],
        'password': decode_base64(args['telegraf_vcenterpwd64']),
        'insecure_skip_verify': True,
        'host_metric_exclude': ['*'],
        'vm_metric_exclude': ['*'],
        'max_query_metrics': 256,
        'collect_concurrency': 3
    }

    # Load the existing TOML file into a dictionary
    try:
        with open(config_file_path, 'r') as file:
            config_content = toml.load(file)
            logging.debug(f"Loaded config_content type: {type(config_content)}")
            logging.debug(f"Loaded config_content: {config_content}")
    except Exception as msgerr:
        logging.error(f"Failed to load telegraf_vmware with error - {msgerr}")
        return -1

    # Ensure config_content is a dictionary
    if not isinstance(config_content, dict):
        logging.error("config_content is not a dictionary, something went wrong.")
        return -1

    # Check if the '[inputs]' section exists, if not, add it
    if 'inputs' not in config_content:
        config_content['inputs'] = {}

    # Remove any existing 'vsphere' sections if they exist
    if 'vsphere' in config_content['inputs']:
        del config_content['inputs']['vsphere']

    # Add the new 'vsphere' sections (realtime and historical)
    config_content['inputs']['vsphere'] = [new_realtime_instance, new_historical_instance]

    # Write the updated content back to the configuration file
    try:
        with open(config_file_path, 'w') as file:
            toml.dump(config_content, file)
    except Exception as msgerr:
        logging.error(f"Failed to write telegraf_vmware with error - {msgerr}")

    logging.debug("Finished telegraf_vmware")

