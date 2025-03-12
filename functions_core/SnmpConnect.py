# EASYSNMP
#hostname – hostname or IP address of SNMP agent
#version – the SNMP version to use; 1, 2 (equivalent to 2c) or 3
#community – SNMP community string (used for both R/W) (v1 & v2)
#timeout – seconds before retry
#retries – retries before failure
#remote_port – allow remote UDP port to be overridden (this will communicate on port 161 at its default setting)
#local_port – allow overriding of the local SNMP port
#security_level – security level (no_auth_or_privacy, auth_without_privacy or auth_with_privacy) (v3)
#security_username – security name (v3)
#privacy_protocol – privacy protocol (v3)
#privacy_password – privacy passphrase (v3)
#auth_protocol – authentication protocol (MD5 or SHA) (v3)
#auth_password – authentication passphrase (v3)

from easysnmp import Session
from functions_core.SshConnect import *
import logging

class SnmpConnect():
    def __init__(self, **args):
        self.status = True
        self.ip = args['ip']
        self.bastion = args['bastion']
        self.snmp_community = args['snmp_community']
        self.snmp_version = args['snmp_version']
        self.snmp_user = args.get('snmp_user')
        self.snmp_password = args.get('snmp_password')
        self.snmp_auth_protocol = args.get('snmp_auth_protocol')
        self.user = args.get('user')
        self.host_keys = args.get('host_keys')

        if self.bastion and self.user and self.host_keys:

            try:
                logging.debug(f"Class SnmpConnect will call Call SecureConnect with ip:{str(self.ip)}, bastion:{self.bastion}, user:{self.user} and host_keys:{self.host_keys}")
                self.ssh = SshConnect(str(self.bastion), None, self.user, self.host_keys)
            except Exception as msgerror:
                logging.error(f"Failed to connect to {ip} with error: {msgerror}")
                self.status = False
            
            # Ensure SNMP commands exist
            stdout = self.ssh.run("/usr/bin/snmpget;echo $?")
            response = stdout.stdout
            if response == 127:
                logging.error(f"Couldn't find the command snmpget: {response}")
                self.status = False
                
            
            stdout = self.ssh.run("/usr/bin/snmpwalk;echo $?")
            response = stdout.stdout
            if response == 127:
                logging.error(f"Couldn't find the command snmpwalk: {response}")
                self.status = False
                return
            
            logging.debug(f"Managed to get ssh tunnel and snmp commands exist id:{self.ssh}")

        elif self.ip and self.snmp_community and self.snmp_version:
            logging.debug(f"Will not use a bastion to connect")

            if (self.snmp_version == '1' or self.snmp_version == "2") and self.ip:
                try:
                    logging.debug(f"Will connect with ip {self.ip} , community {self.snmp_community} , version {self.snmp_version}")
                    self.session = Session(hostname=str(self.ip), community=self.snmp_community, version=int(self.snmp_version))
                except Exception as msgerror:
                    logging.error(f"Failed to open SNMP Connection with version < 3 {self.ip} with error: {msgerror}")
                    self.status = False
                
            elif self.snmp_version == '3' and self.ip and self.snmp_user and self.snmp_password and self.snmp_auth_protocol:
                try:
                    logging.debug(f"Will connect with ip {self.ip} , community {self.snmp_community} , version {self.snmp_version}, user {self.user} , password {self.snmp_password[:2]} , protocol {self.snmp_auth_protocol}")
                    self.session = Session(hostname=str(self.ip), community=self.snmp_community, version=int(self.snmp_version))
                except Exception as msgerror:
                    logging.error(f"Failed to open SNMP Connection with version 3 {self.ip} with error: {msgerror}")
                    self.status = False
            else:
                logging.debug(f"Failed to connect using SNMP, check config - ip {self.ip} , community {self.snmp_community} , version {self.snmp_version}, user {self.user} , password {self.snmp_password[:2]} , protocol {self.snmp_auth_protocol}")
                self.status = False
        else:
            logging.error(f"Failed to connect using SNMP, check config - ip {self.ip} , community {self.snmp_community} , version {self.snmp_version}, user {self.user} , password {self.snmp_password[:2]} , protocol {self.snmp_auth_protocol}")

        logging.debug(f"Create SnmpSession without bastion id")

    def get(self, cmd):
        if self.status is False:
            logging.error("SNMP session is not initialized.")
            self.status = False

        if self.bastion:
            if self.snmp_version == 3 and self.snmp_password:
                stdout = self.ssh.run(f"/usr/bin/snmpget -v {self.snmp_version} -c {self.snmp_community} -u {self.snmp_user} -a {self.snmp_auth_protocol} -A {self.snmp_password} {cmd}")
                return stdout.stdout
            else:
                snmpver = self.snmp_version
                if self.snmp_version == 2:
                    snmpver = "2c"
                logging.debug(f"Cmd is {cmd}")
                stdout = self.ssh.run(f"/usr/bin/snmpget -v  {snmpver} -c {self.snmp_community} {str(self.ip)} {cmd}")
                logging.debug(f"stdout is {stdout}")
                logging.debug(f"stdout.stdout is {stdout.stdout}")

                response = stdout.stdout.split(":", 1)[1].strip()
                logging.debug(f"Response is {response}")
                return response
        else:
            try:
                result = self.session.get(cmd)
                logging.debug(f"result with SNMP get is {result}")
                logging.debug(f"result.value with SNMP get is {result.value}")
                return str(result.value)
            except Exception as e:
                logging.error(f"Failed to get SNMP data for {cmd}: {e}")
                self.status = False

    def walk(self, cmd):
        if self.status is False:
            logging.error("SNMP session is not initialized.")
            self.status = False

        if self.bastion:
            if self.snmp_version == 3 and self.snmp_password:
                stdout = self.ssh.run(f"/usr/bin/snmpwalk -v {self.snmp_version} -c {self.snmp_community} -u {self.snmp_user} -a {self.snmp_auth_protocol} -A {self.snmp_password} {cmd}")
                logging.debug(f"cmd on bastion with SNMP version 1 or walk is {cmd}")
                logging.debug(f"stdout on bastion with SNMP version 1 or walk is {stdout}")
                logging.debug(f"stdout.stdout on bastion with SNMP version 1 walk  is {stdout.stdout}")

                responses=[]
                for line in stdout.stdout.splitlines():
                    response_parts = line.split(":", 1)
                    if len(response_parts) > 1:
                        response = response_parts[1].strip()
                        responses.append(response)
                    else:
                        logging.debug(f"Line does not contain a colon: {line}")

                logging.debug(f"Responses are {responses}")
                return responses
            else:
                snmpver = self.snmp_version
                if self.snmp_version == 2:
                    snmpver = "2c"

                stdout = self.ssh.run(f"/usr/bin/snmpwalk -v {snmpver} -c {self.snmp_community} {str(self.ip)} {cmd}")
                logging.debug(f"cmd on bastion with SNMP version 1 or walk is {cmd}")
                logging.debug(f"stdout on bastion with SNMP version 1 or walk is {stdout}")
                logging.debug(f"stdout.stdout on bastion with SNMP version 1 walk  is {stdout.stdout}")

                responses=[]
                for line in stdout.stdout.splitlines():
                    response_parts = line.split(":", 1)
                    if len(response_parts) > 1:
                        response = response_parts[1].strip()
                        responses.append(response)
                    else:
                        logging.debug(f"Line does not contain a colon: {line}")

                logging.debug(f"Responses are {responses}")
                return responses
        else:
            responses = []
            try:
                result = self.session.walk(cmd)
                logging.debug(f"stdout with SNMP walk is {result}")
            except Exception as e:
                logging.error(f"Failed to process SNMP walk for {cmd}: {e}")
                return None
            
            for item in result:
                # Access the 'value' attribute of the SNMPVariable object
                logging.debug(f"Item is {item}")
                if hasattr(item, "value"):  # Ensure the item has a 'value' attribute
                    logging.debug(f"Item have value attribute {item.value}")
                    response = item.value
                    responses.append(response)
                else:
                    logging.debug(f"Item does not have a 'value' attribute: {item}")
            logging.debug(f"Responses are {responses}")
            return responses



    def rm(self):
        if self.bastion:
            self.ssh.rm()
