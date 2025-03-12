from easysnmp import Session
from functions_core.send_influxdb import *
from functions_core.SnmpConnect import *  

def eternus_dx_cpu(**args):
    # Create an SNMP session to a device
    session = Session(hostname=str(args['ip']), community=str(args['snmp_community']), version=1)
    #session=SnmpConnect(str(args['ip']),args['bastion'],args['snmp_comunity'],args['snmp_version'], args['snmp_user'], args['snmp_password'], args['snmp_auth_protocol'], args['user'], args['host_keys'])
    #ip, bastion, snmp_community, snmp_version, snmp_user, snmp_password, snmp_auth_protocol, user, host_keys

    # We will get the OID version, until now all the rest of the info is the same
    SNMP_MIB_VER = session.get('1.3.6.1.2.1.1.2.0').value[1:]

    timestamp = int(session.get(SNMP_MIB_VER + '.5.1.4.0').value)

    #Core
    # Number of CM's iso.3.6.1.4.1.211.1.21.1.150.5.14.1.0
    # Cores per CM iso.3.6.1.4.1.211.1.21.1.150.5.14.2.1.2

    logging.debug(f"Will get number of CM's ")
    nr_cm = int(session.get(SNMP_MIB_VER + '.5.14.1.0').value)
    logging.debug(f"Number of CM's is {nr_cm}")

    
    record=[]

    for count_cm in range(nr_cm):
        i = 3 # the OID 3 is the core id 0. OID 4 is core id 1 and so on.

        logging.debug(f"Will get number of Cores in CM#{count_cm}")
        oid_query_cores = str(SNMP_MIB_VER + ".5.14.2.1.2." + str(count_cm))


        logging.debug(f"OID to query cores is {str(oid_query_cores)}")
   
        nr_cores = int(session.get(oid_query_cores).value)

        logging.debug(f"CM#{count_cm} have cores#{nr_cores}")

        for count_cores in range(nr_cores):

            oid_query_usage = str(SNMP_MIB_VER + ".5.14.2.1." + str(i) + '.' + str(count_cm))

            logging.debug(f"OID to query usage is {oid_query_usage}")
            
            logging.debug(f"CM#{count_cm} Core#{count_cores} usage is {int(session.get(oid_query_usage).value)}")
            i += 1

            record = record + [
                {"measurement": "eternus_dx_cpu",
                "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname'],
                         "CM": str(count_cm), "Core": str(i-4)
                         },
                "fields": {"busyrate": int(session.get(oid_query_usage).value)},
                "time": timestamp
                }
            ]
    
    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by eternus_dx_cpu:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")

    logging.debug("Finished func_eternus_dx_cpu")

def eternus_dx_tppool(**args):
    # Create an SNMP session to a device
    session = Session(hostname=str(args['ip']), community=str(args['snmp_community']), version=1)

    # We will get the OID version, until now all the rest of the info is the same
    snmp_mib_ver = session.get('1.3.6.1.2.1.1.2.0').value[1:]

    timestamp = int(session.get(snmp_mib_ver + '.5.1.4.0').value)
 

    nr_tppool=[]
    #Perform an SNMP WALK on a subtree
    for item in session.walk(snmp_mib_ver + '.14.5.2.1.1'):
        nr_tppool = nr_tppool + [item.value]
    
    record=[]
    

    for poolnr in nr_tppool:
        total_vol_requested = 0
        for vol in session.walk(snmp_mib_ver + '.14.2.2.1.1'):
            if int(session.get(snmp_mib_ver + '.14.2.2.1.10.' + vol.value).value) == int(poolnr):
                total_vol_requested = total_vol_requested + int(session.get(snmp_mib_ver + '.14.2.2.1.4.' + vol.value).value)

        tppool_total_mb = int(session.get(str(snmp_mib_ver + ".14.5.2.1.3." + str(poolnr))).value)
        tppool_used_mb = int(session.get(str(snmp_mib_ver + ".14.5.2.1.4." + str(poolnr))).value)    
        record = record + [
            {"measurement": "eternus_dx_tppool",
            "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname'],
                     "tppool_nr": str(poolnr)
                     },
            "fields": {"total_capacity": int(tppool_total_mb),
                       "use_capacity": int(tppool_used_mb),
                       "total_size_requested": int(total_vol_requested)    
            },
            "time": timestamp
            }
        ]
    
    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by eternus_dx_tppool:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")

    logging.debug("Finished func_eternus_dx_tppool")

def eternus_dx_power(**args):
    # Create an SNMP session to a device
    session = Session(hostname=str(args['ip']), community=str(args['snmp_community']), version=1)

    # We will get the OID version, until now all the rest of the info is the same
    SNMP_MIB_VER = session.get('1.3.6.1.2.1.1.2.0').value[1:]

    timestamp = int(session.get(SNMP_MIB_VER + '.13.1.2.1.4.0').value)
 
    #Perform an SNMP WALK on a subtree
    if int(session.get(SNMP_MIB_VER + '.13.1.2.1.2.0').value) == 2:
        watt_power = int(session.get(SNMP_MIB_VER + '.13.1.2.1.5.0').value)
        record = [
            {"measurement": "eternus_dx_power",
            "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname'],
                     },
            "fields": {
                "power_watt": int(watt_power)    
            },
            "time": timestamp
            }
        ]

    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by eternus_dx_power:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")

    logging.debug("Finished func_eternus_dx_power")

def eternus_dx_temp(**args):
    # Create an SNMP session to a device
    session = Session(hostname=str(args['ip']), community=str(args['snmp_community']), version=1)

    # We will get the OID version, until now all the rest of the info is the same
    SNMP_MIB_VER = session.get('1.3.6.1.2.1.1.2.0').value[1:]

    timestamp = int(session.get(SNMP_MIB_VER + '.13.3.2.1.4.0').value)
 
    #Perform an SNMP WALK on a subtree
    if int(session.get(SNMP_MIB_VER + '.13.3.2.1.2.0').value) == 2:
        intake_temp = int(session.get(SNMP_MIB_VER + '.13.3.2.1.5.0').value)
        record = [
            {
            "measurement": "eternus_dx_temp",
            "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname'],
                     },
            "fields": {
                "intake_temp": int(intake_temp)},
            "time": timestamp
            }
        ]

    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by eternus_dx_temp:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")

    logging.debug("Finished func_eternus_dx_temp")


def eternus_dx_vol(**args):
    # Create an SNMP session to a device
    session = Session(hostname=str(args['ip']), community=str(args['snmp_community']), version=1)

    # We will get the OID version, until now all the rest of the info is the same
    snmp_mib_ver = session.get('1.3.6.1.2.1.1.2.0').value[1:]

    timestamp = int(session.get(snmp_mib_ver + '.5.1.4.0').value)

    record=[]

    for vol in session.walk(snmp_mib_ver + '.14.2.2.1.1'):
        record = record + [
            {"measurement": "eternus_dx_vol",
            "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname'],
                     "vol_id": str(vol.value)
                     },
            "fields": {"vol_size": int(session.get(snmp_mib_ver + '.14.2.2.1.4.' + vol.value).value),
                       "read_iops": int(session.get(snmp_mib_ver + '.5.2.2.1.2.' + vol.value).value),
                       "write_iops": int(session.get(snmp_mib_ver + '.5.2.2.1.3.' + vol.value).value),
                       "read_throughput": int(session.get(snmp_mib_ver + '.5.2.2.1.6.' + vol.value).value), #MB/s
                       "write_throughput": int(session.get(snmp_mib_ver + '.5.2.2.1.7.' + vol.value).value),#MB/s
                       "read_avg_time": int(session.get(snmp_mib_ver + '.5.2.2.1.10.' + vol.value).value),  #ms
                       "write_avg_time": int(session.get(snmp_mib_ver + '.5.2.2.1.11.' + vol.value).value)  #ms
            },
            "time": timestamp
            }
        ]
    
    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by eternus_dx_vol:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")

    logging.debug("Finished func_eternus_dx_vol")



# POWER
# GET TIME iso.3.6.1.4.1.211.1.21.1.150.13.1.2.1.4.0
# must be 2 to collect iso.3.6.1.4.1.211.1.21.1.150.13.1.2.1.2.0
# Average consumption last hour iso.3.6.1.4.1.211.1.21.1.150.13.1.2.1.5.0 in watt
#

# TEMP
# GET TIME iso.3.6.1.4.1.211.1.21.1.150.13.3.2.1.4.0
# must be 2 to collect iso.3.6.1.4.1.211.1.21.1.150.13.3.2.1.2.0
# Max Temp in last hour iso.3.6.1.4.1.211.1.21.1.150.13.3.2.1.5.0 in celsius 
# 

# Volumes
# Get all volumes iso.3.6.1.4.1.211.1.21.1.150.14.2.2.1.1
# Which pool it belongs iso.3.6.1.4.1.211.1.21.1.150.14.2.2.1.10.VOLNUMBER
# Volume capacity (requested) iso.3.6.1.4.1.211.1.21.1.150.14.2.2.1.4.VOLNUMBER
# Read IOPS iso.3.6.1.4.1.211.1.21.1.150.5.2.2.1.2.VOLNUMBER
# Write IOPS iso.3.6.1.4.1.211.1.21.1.150.5.2.2.1.3.VOLNUMBER
# Read Throughtput iso.3.6.1.4.1.211.1.21.1.150.5.2.2.1.6.VOLNUMBER
# Write Throughtput iso.3.6.1.4.1.211.1.21.1.150.5.2.2.1.7.VOLNUMBER
# Read avg response time iso.3.6.1.4.1.211.1.21.1.150.5.2.2.1.10.VOLNUMBER
# Write avg response time iso.3.6.1.4.1.211.1.21.1.150.5.2.2.1.11.VOLNUMBER

# CA Ports
# Get all ports walk 1.3.6.1.4.1.211.1.21.1.150.5.5.2.1.2 if value 11 it's a CA
# 1.3.6.1.4.1.211.1.21.1.150.5.5.2.1.6 + CA's number thoughput MB's
# 1.3.6.1.4.1.211.1.21.1.150.5.5.2.1.3 + CA's number IOPs

# Need community has a overwrite option and license 