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

class SnmpConnect():
    def __init__(self, ip, bastion, snmp_community, snmp_version, snmp_user, snmp_password, snmp_auth_protocol, user, host_keys):

        self.status = True
        self.ip = ip
        self.bastion = bastion
        self.snmp_community = snmp_community
        
        self.snmp_version = snmp_version
        
        if self.snmp_version == 2:
            snmp_version = "2c"

        self.snmp_user = snmp_user
        self.snmp_password = snmp_password
        self.snmp_auth_protocol = snmp_auth_protocol
        self.user = user
        self.host_keys = host_keys


        if self.bastion:
            try:
                logging.debug(f"Class SnmpConnect will call Call SecureConnect with ip:{str(self.ip)}, bastion:{self.bastion}, user:{self.user} and host_keys:{self.host_keys}")
                self.ssh = SshConnect(str(self.ip), self.bastion, self.user, self.host_keys)
            except Exception as msgerror:
                logging.error(f"Failed to connect to {ip} with error: {msgerror}")
                self.status = False
            
            # Ensure SNMP commands exist
            stdout = self.ssh.run("type snmpget;echo $?")
            response = stdout.stdout
            if response != "0":
                logging.error(f"Couldn't find the command snmpget: {response}")
                self.status = False
                
            
            stdout = self.ssh.run("type snmpwalk;echo $?")
            response = stdout.stdout
            if response != "0":
                logging.error(f"Couldn't find the command snmpwalk: {response}")
                self.status = False
                return
            
            logging.debug(f"Managed to get ssh tunnel and snmp commands exist id:{self.ssh}")

        else:
            logging.debug(f"Will not use a bastion to connect")

            if (self.snmp_version == 1 or self.snmp_version == "2c") and self.ip:
                try:
                    logging.debug(f"Will connect with ip {self.ip} , community {self.snmp_community} , version {self.snmp_version}")
                    self.session = Session(hostname=self.ip, community=self.snmp_community, version=self.snmp_version)
                except Exception as msgerror:
                    logging.error(f"Failed to open SNMP Connection with version < 3 {self.ip} with error: {msgerror}")
                    self.status = False
                    exit -1
            elif self.snmp_version == 3 and self.ip and self.snmp_user and self.snmp_password and self.snmp_auth_protocol:
                try:
                    logging.debug(f"Will connect with ip {self.ip} , community {self.snmp_community} , version {self.snmp_version}, user {self.user} , password {self.snmp_password[:2]} , protocol {self.snmp_auth_protocol}")
                    self.session = Session(hostname=self.ip, community=self.snmp_community, version=self.snmp_version)
                except Exception as msgerror:
                    logging.error(f"Failed to open SNMP Connection with version 3 {self.ip} with error: {msgerror}")
                    self.status = False
                    exit -1
            else:
                logging.debug(f"Failed to connect using SNMP, check config - ip {self.ip} , community {self.snmp_community} , version {self.snmp_version}, user {self.user} , password {self.snmp_password[:2]} , protocol {self.snmp_auth_protocol}")
                exit -1
            
            logging.debug(f"Create SnmpSession without bastion id")

    def get(self, cmd):
        if self.session is None:
            logging.error("SNMP session is not initialized.")
            return None

        if self.bastion:
            if self.snmp_version == 3 and self.snmp_password:
                stdout = self.ssh.run(f"snmpget -v {self.snmp_version} -c {self.snmp_community} -u {self.snmp_user} -a {self.snmp_auth_protocol} -A {self.snmp_password} {cmd}")
                return stdout.stdout
            else:
                stdout = self.ssh.run(f"snmpget -v {self.snmp_version} -c {self.snmp_community} {cmd}")
                return stdout.stdout
        else:
            try:
                result = self.session.get(cmd)
                return str(result.value) if result else None
            except Exception as e:
                logging.error(f"Failed to get SNMP data for {cmd}: {e}")
                return None

    def walk(self, cmd):
        if self.session is None:
            logging.error("SNMP session is not initialized.")
            return None

        if self.bastion:
            if self.snmp_version == 3 and self.snmp_password:
                stdout = self.ssh.run(f"snmpwalk -v {self.snmp_version} -c {self.snmp_community} -u {self.snmp_user} -a {self.snmp_auth_protocol} -A {self.snmp_password} {cmd}")
                return stdout.stdout
            else:
                stdout = self.ssh.run(f"snmpwalk -v {self.snmp_version} -c {self.snmp_community} {cmd}")
                return stdout.stdout
        else:
            try:
                result = self.session.walk(cmd)
                return str(result.value) if result else None
            except Exception as e:
                logging.error(f"Failed to walk SNMP data for {cmd}: {e}")
                return None

    def rm(self):
        if self.bastion:
            self.ssh.rm()
