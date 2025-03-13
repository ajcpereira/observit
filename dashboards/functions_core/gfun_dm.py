#################################################################################
#                                                                               #
#                       IDENTIFICATION DIVISION                                 #
#                                                                               #
#################################################################################
# Module: Grafana Data Model (grafanafun_dm.py)
#
# This module implements the data model that will enable the creation of the
# automated dashboard.
# It will read the yaml configuration file and transforms in a dictionary with
# the following structure:
#
#


#################################################################################
#                                                                               #
#                       ENVIRONMENT DIVISION                                    #
#                                                                               #
#################################################################################
import json, logging


#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################


#################################################################################
#                                                                               #
#                       FUNCTION DIVISION                                      #
#                                                                               #
#################################################################################

def check_alias(alias, ip):
    # Check if Alias is defined, if not use IPAddress for hostname
    if alias:
        hostname = alias
    else:
        hostname = ip

    return hostname


def data_model_system_exists(sys_name, dict):

    for sys in dict:
        if sys['system'] == sys_name:
            logging.debug("Grafana data model: system name %s exists, is new %s", sys_name, False)
            return False, sys

    logging.debug("Grafana data model: system name %s doesnt exists, is new %s, initiate data model with %s"
                   % (sys_name, True, {'system': sys_name, 'resources': []}))

    return True, {'system': sys_name, 'resources': []}


def data_model_resource_exists(res_name, dict):

    for res in dict['resources']:
        if res['name'] == res_name:
            logging.debug("Grafana data model: resource name %s exists, is new %s", res_name, False)
            return False, res

    logging.debug("Grafana data model: resource name %s doesnt exists, is new %s, initiate data model with %s"
                  % (res_name, True, {'system': res_name, 'resources': []}))

    return True, {'name': res_name, 'data': []}


def data_model_metric_exists(met_name, dict):

    for res in dict['data']:
        if res['metric'] == met_name:
            logging.debug("Grafana data model: metric name %s exists, is new %s", met_name, False)
            return False, res

    logging.debug("Grafana data model: metric name %s doesnt exists, is new %s, initiate data model with %s"
                  % (met_name, True, {'metric': met_name, 'hosts': []}))

    return True, {'metric': met_name, 'hosts': []}


def data_model_build(config):

    json_dict = json.loads(config.model_dump_json())
    d_model = []

    logging.debug("%s - Config file in JSON format is: %s" % (data_model_build.__name__,json_dict))

    try:
        for sys in json_dict['systems']:

            # Check if the System already exists in the data model
            new_d_sys, d_sys = data_model_system_exists(sys['name'], d_model)

            # Check if the Resource already exists in the data model
            new_d_res, d_res = data_model_resource_exists(sys['resources_types'], d_sys)

            for metrics in sys['config']['metrics']:
                # Check if the metric already exists in the data model
                new_d_met, d_metric = data_model_metric_exists(metrics['name'], d_res)

                for host in sys['config']['ips']:
                        hostname = check_alias(host['alias'], host['ip'])
                        #d_metric['hosts'] = d_metric['hosts'] + [host['alias']]
                        d_metric['hosts'] = d_metric['hosts'] + [hostname]

                # if the metric doesn't exist new_d_met = True then create new - else it has already been updated do nothing
                if new_d_met:
                    d_res['data'] = d_res['data'] + [d_metric]

            # if the Resource doesn't exist, create new - else it has already been updated do nothing
            if new_d_res:
                d_sys['resources'] = d_sys['resources'] + [d_res]

            # if the System doesn't exist, create new - else it has already been updated do nothing
            if new_d_sys:
                d_model = d_model + [d_sys]

        logging.debug("%s: Grafana_fun data model is: %s" %(data_model_build.__name__, d_model))

    except Exception as msgerror:
        logging.error("%s: Failed to create grafana data model with error %s" %(data_model_build.__name__, msgerror))
        return []

    return d_model


def data_model_get_hosts_per_resource_grouped(json_data):
     # Load JSON data if it's in string format
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    result = {}

    # Iterate over each system to gather data
    for system in json_data:
        system_name = system['system']
        resources = system['resources']
        
        for resource in resources:
            resource_name = resource['name']
            if resource_name not in result:
                result[resource_name] = {}

            # Add hosts to the dictionary for that system and resource
            for metric in resource['data']:
                if system_name not in result[resource_name]:
                    result[resource_name][system_name] = set()  # Use a set to ensure uniqueness

                result[resource_name][system_name].update(metric['hosts'])

    # Convert sets to lists to produce the final result format
    for resource_name in result:
        for system_name in result[resource_name]:
            result[resource_name][system_name] = list(result[resource_name][system_name])

    return result