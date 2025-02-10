import time

from functions_core.http_connect import *
from functions_core.send_influxdb import *
from functions_core.utils import *

#   POWER
#   ['Oem']['ts_fujitsu']['ChassisPowerConsumption']['CurrentPowerConsumptionW']
#   ['Oem']['Hpe']['PowerControl']['']

URI_REDFISH_CHASSIS = 'redfish/v1/Chassis/'


class RedfishOem:
    FUJITSU = 'FUJITSU'
    HPE = 'Hpe'
    CONTOSO = 'Contoso'


def server_power(**args):
    # DEFINITIONS / CONSTANTS

    # REQUEST_HEADER = {'Accept': 'application/json; charset=UTF-8'}

    password = decode_base64(args['redfish_pwd64'])

    logging.debug(
        f"FUNC[{server_power.__name__}]: Arguments are url {args['redfish_url']}, user {args['redfish_user']}, pass {args['redfish_pwd64']}")
    logging.debug(
        f"FUNC[{server_power.__name__}]: Retrieving Chassis list from URL {args['redfish_url']}{URI_REDFISH_CHASSIS}")

    http_client = HttpConnect(args['redfish_url'], args['redfish_user'], password, args['redfish_unsecured'])
    response = http_client.get(URI_REDFISH_CHASSIS)

    power_consumption = 0

    if response is not None:
        json_res = response.json()
        chassis_members = json_res['Members']
        logging.debug(f"FUNC[{server_power.__name__}]: Chassis Members list is {chassis_members}")

        # For the moment we will assume that if there are several Chassis in this system, the power_consumption
        # for the system will be the sum of all the values.

        for member in chassis_members:
            uri = member['@odata.id']
            logging.debug(f"FUNC[{server_power.__name__}]: Retrieving Chassis info from URL {args['redfish_url']}{uri}")
            response = http_client.get(uri)

            if response is not None:
                json_res = response.json()
                power_uri = json_res['Power']['@odata.id']
                vendor = json_res['Manufacturer']

                logging.debug(f"FUNC[{server_power.__name__}]: Retrieved Power URI is {power_uri} ")
                logging.debug(f"FUNC[{server_power.__name__}]: Retrieved Vendor name is {vendor}")

                logging.debug(
                    f"FUNC[{server_power.__name__}]: Retrieving Power info from URL {args['redfish_url']}{uri}")
                response = http_client.get(power_uri)

                if response is not None:
                    json_res = response.json()
                    int_timestamp = int(time.time())
                    logging.debug(
                        f"FUNC[{server_power.__name__}]: Retrieved power information is \033[92m {json_res} \033[00m")
                    match vendor:
                        case RedfishOem.FUJITSU:
                            power_consumption += json_res['Oem']['ts_fujitsu']['ChassisPowerConsumption'][
                                'CurrentPowerConsumptionW']
                            logging.debug(
                                f"FUNC[{server_power.__name__}]: Total PowerConsumedWatts is {power_consumption}")

                        case _:
                            logging.debug(
                                f"FUNC[{server_power.__name__}]: "
                                f"Reading from PowerControl is {json_res['PowerControl']}")
                            for powerC in json_res['PowerControl']:
                                power_consumption += powerC['PowerConsumedWatts']
                            logging.debug(
                                f"FUNC[{server_power.__name__}]: Total PowerConsumedWatts is {power_consumption}")

                else:
                    logging.error(
                        f"FUNC[{server_power.__name__}]: Error Retrieving Power info from URL {args['redfish_url']}{uri}")
                    return -1
            else:
                logging.error(
                    f"FUNC[{server_power.__name__}]: Error Retrieving Chassis info from URL {args['redfish_url']}{uri}")
                return -1

        # Write data to influx DB

        # int_timestamp = int(time.time())

        influxdb_record = [
            {"measurement": "power",
             "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname']},
             "fields": {"PowerConsumedWatts": power_consumption},
             "time": int_timestamp
             }
        ]

        # Send Data to InfluxDB
        send_influxdb(str(args['repository']),
                      str(args['repository_port']),
                      args['repository_api_key'],
                      args['repo_org'],
                      args['repo_bucket'],
                      influxdb_record
                      )

        http_client.close()

    else:
        logging.error(
            f"FUNC[{server_power.__name__}]: Error Retrieving Chassis list from URL {args['redfish_url']}{URI_REDFISH_CHASSIS}")
        return -1


def server_temp(**args):
    # DEFINITIONS / CONSTANTS

    # REQUEST_HEADER = {'Accept': 'application/json; charset=UTF-8'}

    password = decode_base64(args['redfish_pwd64'])

    logging.debug(
        f"FUNC[{server_temp.__name__}]: Arguments are url {args['redfish_url']}, user {args['redfish_user']}, pass {args['redfish_pwd64']}")
    logging.debug(
        f"FUNC[{server_temp.__name__}]: Retrieving Chassis list from URL {args['redfish_url']}{URI_REDFISH_CHASSIS}")

    http_client = HttpConnect(args['redfish_url'], args['redfish_user'], password, args['redfish_unsecured'])
    response = http_client.get(URI_REDFISH_CHASSIS)

    if response is not None:
        json_res = response.json()
        chassis_members = json_res['Members']
        logging.debug(f"FUNC[{server_temp.__name__}]: Chassis Members list is {chassis_members}")

        # For the moment we will assume that if there are several Chassis in this system, the power_consumption
        # for the system will be the sum of all the values.

        for member in chassis_members:
            uri = member['@odata.id']
            logging.debug(f"FUNC[{server_temp.__name__}]: Retrieving Chassis info from URL {args['redfish_url']}{uri}")
            response = http_client.get(uri)

            if response is not None:
                json_res = response.json()
                thermal_uri = json_res['Thermal']['@odata.id']
                vendor = json_res['Manufacturer']

                logging.debug(f"FUNC[{server_temp.__name__}]: Retrieved Thermal URI is {thermal_uri} ")
                logging.debug(f"FUNC[{server_temp.__name__}]: Retrieved Vendor name is {vendor}")

                logging.debug(
                    f"FUNC[{server_temp.__name__}]: Retrieving Thermal info from URL {args['redfish_url']}{uri}")
                response = http_client.get(thermal_uri)

                if response is not None:
                    json_res = response.json()
                    logging.debug(
                        f"FUNC[{server_temp.__name__}]: Retrieved Thermal information is \033[92m {json_res} \033[00m")

                    intake_temp = None
                    for temp in json_res['Temperatures']:
                        if temp['PhysicalContext'] == "Intake":
                            intake_temp = temp['ReadingCelsius']
                            int_timestamp = int(time.time())
                            break
                    logging.debug(
                        f"FUNC[{server_temp.__name__}]: Intake Temperature is {intake_temp}")

                else:
                    logging.error(
                        f"FUNC[{server_temp.__name__}]: Error Retrieving Thermal info from URL {args['redfish_url']}{uri}")
                    return -1
            else:
                logging.error(
                    f"FUNC[{server_temp.__name__}]: Error Retrieving Chassis info from URL {args['redfish_url']}{uri}")
                return -1

        # Write data to influx DB


        influxdb_record = [
            {"measurement": "temp",
             "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname']},
             "fields": {"AmbTemp": intake_temp},
             "time": int_timestamp
             }
        ]

        # Send Data to InfluxDB
        send_influxdb(str(args['repository']),
                      str(args['repository_port']),
                      args['repository_api_key'],
                      args['repo_org'],
                      args['repo_bucket'],
                      influxdb_record
                      )

        http_client.close()

    else:
        logging.error(
            f"FUNC[{server_temp.__name__}]: Error Retrieving Chassis list from URL {args['redfish_url']}{URI_REDFISH_CHASSIS}")
        return -1



def server_power_ai(**args):
    password = decode_base64(args['redfish_pwd64'])
    logging.debug(f"FUNC[{server_power.__name__}]: Arguments are url {args['redfish_url']}, user {args['redfish_user']}, pass {args['redfish_pwd64']}")

    http_client = HttpConnect(args['redfish_url'], args['redfish_user'], password, args['redfish_unsecured'])
    response = http_client.get(URI_REDFISH_CHASSIS)

    if response is None:
        logging.error(f"FUNC[{server_power.__name__}]: Error Retrieving Chassis list from URL {args['redfish_url']}{URI_REDFISH_CHASSIS}")
        return -1

    power_consumption = 0
    chassis_members = response.json().get('Members', [])
    logging.debug(f"FUNC[{server_power.__name__}]: Chassis Members list is {chassis_members}")

    for member in chassis_members:
        uri = member['@odata.id']
        logging.debug(f"FUNC[{server_power.__name__}]: Retrieving Chassis info from URL {args['redfish_url']}{uri}")
        response = http_client.get(uri)

        if response is None:
            logging.error(f"FUNC[{server_power.__name__}]: Error Retrieving Chassis info from URL {args['redfish_url']}{uri}")
            return -1

        chassis_info = response.json()
        power_uri = chassis_info['Power']['@odata.id']
        vendor = chassis_info['Manufacturer']

        logging.debug(f"FUNC[{server_power.__name__}]: Retrieved Power URI is {power_uri}")
        logging.debug(f"FUNC[{server_power.__name__}]: Retrieved Vendor name is {vendor}")

        response = http_client.get(power_uri)
        if response is None:
            logging.error(f"FUNC[{server_power.__name__}]: Error Retrieving Power info from URL {args['redfish_url']}{power_uri}")
            return -1

        power_info = response.json()
        int_timestamp = int(time.time())
        logging.debug(f"FUNC[{server_power.__name__}]: Retrieved power information is \033[92m {power_info} \033[00m")

        if vendor == RedfishOem.FUJITSU:
            power_consumption += power_info['Oem']['ts_fujitsu']['ChassisPowerConsumption']['CurrentPowerConsumptionW']
        else:
            for powerC in power_info['PowerControl']:
                power_consumption += powerC['PowerConsumedWatts']

        logging.debug(f"FUNC[{server_power.__name__}]: Total PowerConsumedWatts is {power_consumption}")

    influxdb_record = [{
        "measurement": "power",
        "tags": {
            "system": args['name'],
            "resource_type": args['resources_types'],
            "host": args['hostname']
        },
        "fields": {"PowerConsumedWatts": power_consumption},
        "time": int_timestamp
    }]

    send_influxdb(
        str(args['repository']),
        str(args['repository_port']),
        args['repository_api_key'],
        args['repo_org'],
        args['repo_bucket'],
        influxdb_record
    )

    http_client.close()
