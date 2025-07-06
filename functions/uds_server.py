import time
from datetime import datetime
from functions_core.HttpConnect import *
from functions_core.send_influxdb import *
from functions_core.utils import *


def uds_server_servicepools(**args):

    logging.debug(f"Arguments are url {args['uds_server_url']}, user {args['uds_server_user']} pass {args['uds_server_password_pwd64'][4]} and unsecure {args['uds_server_unsecured']}")

    password = decode_base64(args['uds_server_password_pwd64'])

    rest_url_path = 'uds/rest/'

    # STEP 1: UDS server login
    request_url_path = rest_url_path + 'auth/login'
    request_body = {
        "auth": args['uds_server_auth'],
        "username": args['uds_server_user'],
        "password": password
    }

    http_client = HttpConnect(base_url=args['uds_server_url'], unsecured=args['uds_server_unsecured'])
    response = http_client.post(request_url_path, data=request_body)

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        logging.debug(f"Login response: {response_json}")
    except Exception as e:
        logging.error(f"Login response: {response.content} {response.headers['Date']}")
        logging.error(f"Error parsing login response: {e}")
        return -1

    # Check login result
    if response_json.get('result') != "ok":
        logging.error(f"Login failed. Response: {response_json}")
        return -1
        
    session_auth = response_json.get('token')
    print(session_auth)

    #STEP 2: retrieve service pools
    #
    #
    request_url_path = rest_url_path + 'servicespools/overview'
    response = http_client.get(request_url_path, headers={"X-Auth-Token": session_auth })

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        date_str = response.headers['Date']
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
        timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S.00Z")
        logging.debug(f"Service pools request json response: {response_json}")
    except Exception as e:
        logging.error(f"Error parsing login response: {e}")
        return -1

    for pool in response_json:
        #print(pool['name'], pool['initial_srvs'], pool['max_srvs'], pool['info']['servicesTypeProvided'][0] )

        influxdb_record = [{
             "measurement": "uds_server_servicepool",
             "tags": {
                "system": args['name'],
                "resource_type": args['resources_types'],
                "host": args['hostname'],
                "id": pool['id'],
                "name": pool['name'],
                #must check versio in the future
                #"servicesTypeProvided": pool['info']['services_type_provided'],
                "servicesTypeProvided": pool['info']['services_type_provided'] if 'services_type_provided' in pool['info'] else 'unknown',
              },
             "fields": {
                "initial_srvs": pool['initial_srvs'],
                "max_srvs": pool['max_srvs'],
                "cache_l1_srvs": pool['cache_l1_srvs'],
                "cache_l2_srvs": pool['cache_l2_srvs'],
                "user_services_count": pool['user_services_count'],
                "user_services_in_preparation": pool['user_services_in_preparation'],
                "usage": float(pool['usage'].strip('%')),
             },
             "time": timestamp,
         }
        ]

        logging.debug(f"Data to be sent to influxdb {influxdb_record}")

        send_influxdb(
            str(args['repository']),
            str(args['repository_port']),
            args['repository_api_key'],
            args['repo_org'],
            args['repo_bucket'],
            influxdb_record
        )
        
    #STEP 3: logout
    #
    #
    request_url_path = rest_url_path + 'auth/logout'
    response = http_client.get(request_url_path, headers={"X-Auth-Token": session_auth })

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        logging.debug(f"Logout response: {response_json}")
    except Exception as e:
        logging.error(f"Error parsing logout response: {e}")
        return -1

    http_client.close()

    return 1



def uds_server_authenticators(**args):

    logging.debug(f"Arguments are url {args['uds_server_url']}, user {args['uds_server_user']} pass {args['uds_server_password_pwd64'][4]} and unsecure {args['uds_server_unsecured']}")

    password = decode_base64(args['uds_server_password_pwd64'])

    rest_url_path = 'uds/rest/'

    # STEP 1: UDS server login
    request_url_path = rest_url_path + 'auth/login'
    request_body = {
        "auth": args['uds_server_auth'],
        "username": args['uds_server_user'],
        "password": password
    }

    http_client = HttpConnect(base_url=args['uds_server_url'], unsecured=args['uds_server_unsecured'])
    response = http_client.post(request_url_path, data=request_body)

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        logging.debug(f"Login response: {response_json}")
    except Exception as e:
        logging.error(f"Login response: {response.content} {response.headers['Date']}")
        logging.error(f"Error parsing login response: {e}")
        return -1

    # Check login result
    if response_json.get('result') != "ok":
        logging.error(f"Login failed. Response: {response_json}")
        return -1
        
    session_auth = response_json.get('token')
    print(session_auth)

    #STEP 2: retrieve authenticators
    #
    #
    request_url_path = rest_url_path + 'authenticators/overview'
    response = http_client.get(request_url_path, headers={"X-Auth-Token": session_auth })

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        date_str = response.headers['Date']
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
        timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S.00Z")
        logging.debug(f"Authenticators pools request json response: {response_json}")
    except Exception as e:
        logging.error(f"Error parsing Authenticators response: {e}")
        return -1

    for auth in response_json:
        
        influxdb_record = [{
             "measurement": "uds_server_authenticators",
             "tags": {
                "system": args['name'],
                "resource_type": args['resources_types'],
                "host": args['hostname'],
                "id": auth['id'],
                "name": auth['name'],
              },
             "fields": {
                "users_count": auth['users_count'],
             },
             "time": timestamp,
         }
        ]

        logging.debug(f"Data to be sent to influxdb {influxdb_record}")

        send_influxdb(
            str(args['repository']),
            str(args['repository_port']),
            args['repository_api_key'],
            args['repo_org'],
            args['repo_bucket'],
            influxdb_record
        )
        
    #STEP 3: logout
    #
    #
    request_url_path = rest_url_path + 'auth/logout'
    response = http_client.get(request_url_path, headers={"X-Auth-Token": session_auth })

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        logging.debug(f"Logout response: {response_json}")
    except Exception as e:
        logging.error(f"Error parsing logout response: {e}")
        return -1

    http_client.close()

    return 1


def uds_server_system_overview(**args):

    logging.debug(f"Arguments are url {args['uds_server_url']}, user {args['uds_server_user']} pass {args['uds_server_password_pwd64'][4]} and unsecure {args['uds_server_unsecured']}")

    password = decode_base64(args['uds_server_password_pwd64'])

    rest_url_path = 'uds/rest/'

    # STEP 1: UDS server login
    request_url_path = rest_url_path + 'auth/login'
    request_body = {
        "auth": args['uds_server_auth'],
        "username": args['uds_server_user'],
        "password": password
    }

    http_client = HttpConnect(base_url=args['uds_server_url'], unsecured=args['uds_server_unsecured'])
    response = http_client.post(request_url_path, data=request_body)

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        logging.debug(f"Login response: {response_json}")
    except Exception as e:
        logging.error(f"Login response: {response.content} {response.headers['Date']}")
        logging.error(f"Error parsing login response: {e}")
        return -1

    # Check login result
    if response_json.get('result') != "ok":
        logging.error(f"Login failed. Response: {response_json}")
        return -1
        
    session_auth = response_json.get('token')
    print(session_auth)

    #STEP 2: retrieve service pools
    #
    #
    request_url_path = rest_url_path + 'system/overview'
    response = http_client.get(request_url_path, headers={"X-Auth-Token": session_auth })

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        date_str = response.headers['Date']
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
        timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S.00Z")
        logging.debug(f"System Overview request json response: {response_json}")
    except Exception as e:
        logging.error(f"Error parsing login response: {e}")
        return -1

    for pool in response_json:
        #print(pool['name'], pool['initial_srvs'], pool['max_srvs'], pool['info']['servicesTypeProvided'][0] )

        influxdb_record = [{
             "measurement": "uds_server_system_overview",
             "tags": {
                "system": args['name'],
                "resource_type": args['resources_types'],
                "host": args['hostname'],
             },
             "fields": {
                "users": pool['users'],
                "users_with_services": pool['users_with_services'],
                "groups": pool['groups'],
                "services": pool['services'],
                "service_pools": pool['service_pools'],
                "meta_pools": pool['meta_pools'],
                "user_services": pool['user_services'],
                "assigned_user_services": pool['assigned_user_services'],
                "restrained_services_pools": pool['restrained_services_pools'],
                "os_managers": pool['os_managers'],
                "transports": pool['transports'],
                "networks": pool['networks'],
                "calendars": pool['calendars'],
                "tunnels": pool['tunnels'],
                "authenticators": pool['authenticators']
             },
             "time": timestamp,
         }
        ]

        logging.debug(f"Data to be sent to influxdb {influxdb_record}")

        send_influxdb(
            str(args['repository']),
            str(args['repository_port']),
            args['repository_api_key'],
            args['repo_org'],
            args['repo_bucket'],
            influxdb_record
        )
        
    #STEP 3: logout
    #
    #
    request_url_path = rest_url_path + 'auth/logout'
    response = http_client.get(request_url_path, headers={"X-Auth-Token": session_auth })

    # Attempt to parse response as JSON
    try:
        response_json = response.json()
        logging.debug(f"Logout response: {response_json}")
    except Exception as e:
        logging.error(f"Error parsing logout response: {e}")
        return -1

    http_client.close()

    return 1
