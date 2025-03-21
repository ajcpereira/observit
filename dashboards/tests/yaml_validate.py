#################################################################################
#                                                                               #
#                       ENVIRONMENT DIVISION                                    #
#                                                                               #
#################################################################################
import yaml
from typing import List, Literal, Optional
from pydantic import BaseModel, StrictStr, PositiveInt, Field, HttpUrl, Base64Str
from pydantic.networks import IPvAnyAddress
import os,logging,sys

#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

########## LIST OF RESOURCES_CONFIGS THAT RUN ONLY ONCE

excluded_resources_types = ["telegraf_local_cpu","telegraf_vmware"]
 
########## LIST OF RESOURCES_CONFIGS THAT RUN ONLY ONCE
#################################################################################
#                                                                               #
#                       PROCEDURE DIVISION                                      #
#                                                                               #
#################################################################################

########## FUNCTION GET AND CHECK CONFIG FILE  ##################################
def configfile_read(configfile):
    try:
        if os.path.isfile(configfile):
            logging.debug("Using default configfile config/config.yaml")
            config = read_yaml(configfile)
            orig_mtime=(os.path.getmtime(configfile))
    except Exception as msgerr:
            logging.error("Can't handle configfile - %s - with error - %s" % (configfile,msgerr))
            sys.exit()

    if 'config' not in locals():
        sys.exit("No configfile could be found")
        
    return config, orig_mtime, configfile
########## FUNCTION GET AND CHECK CONFIG FILE  ##################################

########## CLASS VALIDATES MIXING OF RESOURCE TYPES AND METRICS FROM YAML #######
class AllowedMetrics:
    allowed_metrics = {
        'eternus_cs8000': [['fs_io','fs', 'cpu', 'mem', 'drives', 'medias', 'pvgprofile', 'net', 'fc', 'vtldirtycache'],
                           ['eternus_cs8000.eternus_cs8000_fs_io',
                            'linux_os.linux_os_fs','linux_os.linux_os_cpu', 'linux_os.linux_os_mem', 'eternus_cs8000.eternus_cs8000_drives', 
                            'eternus_cs8000.eternus_cs8000_medias', 'eternus_cs8000.eternus_cs8000_pvgprofile', 'linux_os.linux_os_net', 
                            'eternus_cs8000.eternus_cs8000_fc','eternus_cs8000_vtldirtycache']],
        'linux_os': [['cpu', 'mem', 'fs', 'net'],
                     ['linux_os.linux_os_cpu', 'linux_os.linux_os_mem', 'linux_os.linux_os_fs', 'linux_os.linux_os_net']],
        'server': [['power','temp'], 
                   ['server.server_power','server.server_temp']],
        'powerstore': [['node','space'], 
                   ['powerstore.powerstore_node','powerstore.powerstore_space']],
        'eternus_dx': [['cpu', 'tppool', 'power','temp','vol'], 
                   ['eternus_dx.eternus_dx_cpu', 'eternus_dx.eternus_dx_tppool', 'eternus_dx.eternus_dx_power','eternus_dx.eternus_dx_temp','eternus_dx.eternus_dx_vol']],
        'telegraf_vmware': [['all'], 
                   ['telegraf.telegraf_vmware']],
        'telegraf_local_cpu': [['all'], 
                   ['telegraf.telegraf_local_cpu']]
    }

    @classmethod
    def get_func_name(self, resource_type, metric_name):
    
        metrics_list = self.allowed_metrics.get(resource_type)
        
        try:
            if metric_name in metrics_list[0]:
                index = metrics_list[0].index(metric_name)
        except TypeError:
            logging.error("Selected resource_type - %s - is not allowed, values can be one of the following keys - %s" % (resource_type, self.allowed_metrics.keys()))
            exit()            

        if metric_name in metrics_list[0]:
            index = metrics_list[0].index(metric_name)
            return metrics_list[1][index]
        else:
            logging.error("Selected metric - %s - is not allowed for this resource_type - %s - allowed values are - %s" % (metric_name, resource_type, metrics_list[0]))
            exit()
########## CLASS VALIDATES MIXING OF RESOURCE TYPES AND METRICS FROM YAML #######

########## CLASS FROM PYDANTIC TO VALIDATE YAML SCHEMA ##########################
class Ip(BaseModel):
    ip: IPvAnyAddress
    alias: Optional[StrictStr] = None
    ip_user: Optional[StrictStr] = Field(None)
    ip_snmp_community:Optional[str] = Field("public", max_length=100)
    ip_snmp_version: Optional[Literal['1', '2', '3']] = Field("1")
    ip_snmp_user:Optional[StrictStr] = Field(None) 
    ip_snmp_password:Optional[Base64Str] = Field(None)
    ip_snmp_auth_protocol:Optional[Literal['MD5', 'SHA']] = Field(None)
    ip_use_sudo: Optional[bool] = None
    ip_host_keys: Optional[str] = Field(None, max_length=100)
    ip_bastion: Optional[IPvAnyAddress] = Field(None)
    ip_redfish_url: Optional[HttpUrl] = Field(None)
    ip_redfish_user: Optional[StrictStr] = Field(None)
    ip_redfish_pwd64: Optional[Base64Str] = Field(None)
    ip_redfish_unsecured: Optional[bool] = Field(False)    
    ip_powerstore_url: Optional[HttpUrl] = Field(None)
    ip_powerstore_user: Optional[StrictStr] = Field(None)
    ip_powerstore_pwd64: Optional[Base64Str] = Field(None)
    ip_powerstore_unsecured: Optional[bool] = Field(False)    

class Parameters(BaseModel):
    user: Optional[StrictStr] = Field(None)
    host_keys: Optional[str] = Field(None, max_length=100)
    poll: PositiveInt = Field(..., ge=1, le=1440)
    use_sudo: Optional[bool] = None
    snmp_community:Optional[str] = Field("public", max_length=100)
    snmp_version: Optional[Literal['1', '2', '3']] = Field(None)
    snmp_user:Optional[StrictStr] = Field(None) 
    snmp_password:Optional[Base64Str] = Field(None)
    snmp_auth_protocol:Optional[Literal['MD5', 'SHA']] = Field(None)
    bastion: Optional[IPvAnyAddress] = Field(None)
    ism_server: Optional[IPvAnyAddress] = Field(None)
    ism_password: Optional[str] = Field(None)
    ism_port: Optional[PositiveInt] = Field(None, ge=1, le=65535)
    ism_unsecured: Optional[bool] = Field(False)
    redfish_url: Optional[HttpUrl] = Field(None)
    redfish_user: Optional[StrictStr] = Field(None)
    redfish_pwd64: Optional[Base64Str] = Field(None)
    redfish_unsecured: Optional[bool] = Field(False)
    powerstore_url: Optional[HttpUrl] = Field(None)
    powerstore_user: Optional[StrictStr] = Field(None)
    powerstore_pwd64: Optional[Base64Str] = Field(None)
    powerstore_unsecured: Optional[bool] = Field(False)
    telegraf_vcenterurl: Optional[HttpUrl] = Field(None)
    telegraf_vcenteruser: Optional[StrictStr] = Field(None)   
    telegraf_vcenterpwd64: Optional[Base64Str] = Field(None) 

class Metrics(BaseModel):
    name: StrictStr

class Config(BaseModel):
    parameters: Parameters
    metrics: List[Metrics]
    ips: List[Ip]

class SystemsName(BaseModel):
    name: StrictStr
    resources_types: StrictStr
    config: Config

class GlobalParameters(BaseModel):
    repository: Literal['influxdb']
    repository_port: PositiveInt
    repository_protocol: Literal['tcp']
    repository_api_key: Optional[str] = Field(None)
    loglevel: Literal['NOTSET', 'INFO', 'WARNING', 'DEBUG', 'ERROR', 'CRITICAL']
    logfile: StrictStr
    auto_fungraph: Optional[bool] = False
    grafana_api_key: StrictStr
    grafana_server: Optional[str] = Field('grafana')

class ConfigFile(BaseModel):
    systems: List[SystemsName]
    global_parameters: GlobalParameters
########## CLASS FROM PYDANTIC TO VALIDATE YAML SCHEMA ##########################

########## FUNCTION VALIDATES YAML AND RETURNS DICT #############################
def create_metric_ip_dicts(config):
    result_dicts = []
    global_parms = config.global_parameters
    for system in config.systems:
        for metric in system.config.metrics:
            for ip in system.config.ips:
                ip_dict = vars(ip)
                result_dict = {
                    "name": system.name,
                    "resources_types": system.resources_types,
                    **system.config.parameters.model_dump(),
                    "metric_name": metric.name,
                    "ip": ip.ip,
                    **ip_dict,
                    "func": AllowedMetrics.get_func_name(system.resources_types, metric.name),
                    **global_parms.model_dump(),
                    "repo_org": "observit",
                    "repo_bucket": "observit",
                    "excluded_resources_types_run": 1
                }
                result_dicts.append(result_dict)
              
    return result_dicts, global_parms.model_dump()
########## FUNCTION VALIDATES YAML AND RETURNS DICT #############################

########## FUNCTION READ YAML AND PASS IT TO PYDANTIC CLASS #####################
def read_yaml(file_path: str) -> ConfigFile:
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    
    return ConfigFile(**config)
########## FUNCTION READ YAML AND PASS IT TO PYDANTIC CLASS #####################