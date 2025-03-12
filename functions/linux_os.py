import time

from functions_core.SshConnect import *
from functions_core.send_influxdb import *
import re, logging


#################################################################################
#
#  linux_os_cpu()
#   collects:
#       cpu.use
#       cpu.iowait
#       cpu.load1m
#       cpu.load5m
#       cpu.load15m
#################################################################################

def linux_os_cpu(**args):
    # Definitions/Constants


    bastion = args['bastion']
    host_keys = args['host_keys']
    hostname = args['hostname']

    #unix bash command to be executed
    STR_CMD = "echo $(vmstat 1 2 | tail -1 | awk '{print $15, $16}') $(cat /proc/loadavg | awk '{print $1, $2, $3}')"

    try:
        logging.debug("linux_os_cpu: Starting ssh execution to get linux_os_cpu metrics")

        logging.debug("linux_os_cpu: Connecting to remote host - %s", str(args['ip']))
        logging.debug("linux_os_cpu: Executing command - %s", STR_CMD)

        ssh = SshConnect(str(args['ip']), bastion, args['user'], host_keys)
        stdout = ssh.run(STR_CMD)
        response = stdout.stdout
        ssh.rm()

        # int_timestamp = int(time.time_ns())
        int_timestamp = int(time.time())
        logging.debug("linux_os_cpu: Command Result - %s", response)
        logging.debug("linux_os_cpu: Finished ssh execution to get metrics")

        field = response.split()

        # convert cpu free to in use
        field[0] = 100 - int(field[0])

        # Build dictionary data to influx
        record = [
            {"measurement": "cpu",
             "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname},
             "fields": {"use": int(field[0]), "iowait": int(field[1]), "load1m": float(field[2]), "load5m": float(field[3]),
                        "load15m": float(field[4])},
             "time": int_timestamp
             }
        ]

        logging.debug("linux_os_cpu: Data to be sent to influxdb %s", record)

        # Send Data to InfluxDB
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)

        logging.debug("linux_os_cpu: Ended collecting data")

    #
    except Exception as msgerror:
        logging.error("linux_os_cpu: Failed to collect data from %s with error %s" % (args['ip'], msgerror))
        return -1


###################################################################################
#
#  linux_os_mem()
#       collects memory stats in MB:
#       "mem.total", "mem.used", "mem.free", "mem.shared", "mem.buff", "mem.avail"
###################################################################################
def linux_os_mem(**args):

    bastion = args['bastion']
    host_keys = args['host_keys']
    hostname = args['hostname']

    # unix bash command to be executed
    STR_CMD = "free -m | grep Mem | awk '{print $2, $3, $4, $5, $6, $7}'"

    logging.debug("linux_os_mem: Starting ssh execution to get linux_os_mem metrics")

    logging.debug("linux_os_mem: Connecting to remote host - %s", str(args['ip']))
    logging.debug("linux_os_mem: Executing command - %s", STR_CMD)

    try:
        ssh = SshConnect(str(args['ip']), bastion, args['user'], host_keys)
        stdout = ssh.run(STR_CMD)
        response = stdout.stdout
        ssh.rm()

        int_timestamp = int(time.time())
        logging.debug("linux_os_mem: Command Result - %s", response)
        logging.debug("linux_os_mem: Finished ssh execution to get metrics")

        field = response.split()

        # Build dictionary data to influx
        # ["mem.total", "mem.used", "mem.free", "mem.shared", "mem.buff", "mem.avail"]

        record = [
            {"measurement": "mem",
             "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname},
             "fields": {"total": float(field[0]), "used": float(field[1]), "free": float(field[2]),
                        "shared": float(field[3]), "buff": float(field[4]), "avail": float(field[5])},
             "time": int_timestamp
             }
        ]

        logging.debug("linux_os_mem: Data to be sent to influxdb %s", record)

        # Send Data to InfluxDB
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)

        logging.debug("linux_os_mem: Ended collecting data")

    except Exception as msgerror:
        logging.error("linux_os_mem: Failed to collect data from %s with error %s" % (args['ip'], msgerror))
        return -1


#################################################################################
#
#  linux_os_fs()
#   collects for each filesystem values in KB:
#       "fs.{mount}.available", "fs.{mount}.used", "fs.{mount}.total"

#
#################################################################################
def linux_os_fs(**args):

    bastion = args['bastion']
    host_keys = args['host_keys']
    hostname = args['hostname']

    # unix bash command to be executed
    STR_CMD = "df -x tmpfs -x devtmpfs | tail -n +2 | awk '{print $6, $4, $3, $2}'"

    logging.debug("linux_os_fs: Starting ssh execution to get linux_os_fs filesystem metrics")

    logging.debug("linux_os_fs: Connecting to remote host - %s", str(args['ip']))
    logging.debug("linux_os_fs: Executing command - %s", STR_CMD)

    try:
        sshcon = SshConnect(str(args['ip']), bastion, args['user'], host_keys)
        stdout = sshcon.run(STR_CMD)
        response = stdout.stdout
        sshcon.rm()

        int_timestamp = int(time.time())
        logging.debug("linux_os_fs: Command Result - %s", response)
        logging.debug("linux_os_fs: Finished ssh execution to get linux_os_fs metrics")

        fields = response.splitlines()
        record = []

        # ["fs.mount", "fs.available", "fs.used", "fs.total"] / values in KB

        for line in fields:
            field = str(line).split()
            record = record + [
                {"measurement": "fs",
                 "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname,
                          "mount": field[0]},
                 "fields": {"available": float(field[1]), "used": float(field[2]), "total": float(field[3])},
                 "time": int_timestamp
                 }
            ]

        logging.debug("linux_os_fs: Data to be sent to influxdb %s", record)

        # Send Data to InfluxDB
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)

        logging.debug("linux_os_fs: Ended collecting data")

    except Exception as msgerror:
        logging.error("linux_os_fs: Failed to collect data from %s with error %s" % (args['ip'], msgerror))
        return -1


#################################################################################
#
#  linux_os_net()
#   collects for each network interface in status connected values in Mbp:
#       "net.{iface}.rx_mbp", "net.{iface}.tx_mbp"
#
#################################################################################
def linux_os_net(**args):
    # Network
    # interface  rx_bytes tx_bytes

    bastion = args['bastion']
    host_keys = args['host_keys']
    hostname = args['hostname']

    # unix bash command to be executed
    STR_CMD = "tail -n +3 /proc/net/dev | awk '{sub(/:/, \"\");print $1, $2, $10}'"

    logging.debug("linux_os_net: Starting ssh execution to get linux_os_net network metrics")

    logging.debug("linux_os_net: Connecting to remote host - %s", str(args['ip']))
    logging.debug("linux_os_net: Executing command - %s", STR_CMD)

    try:
        sshcon = SshConnect(str(args['ip']), bastion, args['user'], host_keys)
        stdout = sshcon.run(STR_CMD)
        response = stdout.stdout
        sshcon.rm()

        int_timestamp = int(time.time())
        logging.debug("linux_os_net: Command Result linux_os_net - %s", response)
        logging.debug("linux_os_net: Finished ssh execution to get metrics")

        fields = response.splitlines()
        record = []

        # [interface.if  interface.rx_bytes interface.tx_bytes]

        for line in fields:
            field = str(line).split()
            record = record + [
                {"measurement": "net",
                 "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname,
                          "if": field[0]},
                 "fields": {"rx_bytes": float(field[1]), "tx_bytes": float(field[2])},
                 "time": int_timestamp
                 }
            ]

        logging.debug("linux_os_net: Data to be sent to influxdb %s", record)

        # Send Data to InfluxDB
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)

        logging.debug("linux_os_net: Ended collecting data")

    except Exception as msgerror:
        logging.error("linux_os_net: Failed to collect data from %s with error %s" % (args['ip'], msgerror))
        return -1
