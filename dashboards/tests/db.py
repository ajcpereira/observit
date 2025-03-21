from GfunConfigDB import *
from utils import *
from yaml_validate import *
import pandas


configfile = "/opt/observit/collector/config/config.yaml"

config, orig_mtime, configfile_running = configfile_read(configfile)

config_db = GfunConfigDB(config)


# systems = config_db.run_sql_query("SELECT DISTINCT system FROM config")

# df = config_db.get_distinct_rows()

# print(f"{df}")

hosts = config_db.run_sql_query("SELECT DISTINCT system, resource_type, host FROM config ORDER BY system, resource_type, host")
hosts = config_db.run_sql_query("SELECT DISTINCT * FROM config ORDER BY system, resource_type, host")

print(hosts)
# for index, row in hosts.iterrows():
#     print(f"gfun_host_{row["resource_type"]}_{row["metric"]}({row["system"], row["host"]})")

#print(f"{hosts}")


exit(1)

df = config_db.get_metrics_for_host_system("IMBKCS8002", "eternus_cs8000", "VLP")

print(f"{df}")

systems = config_db.get_system_list

for system in config_db.get_system_list():
    for resource_type in config_db.get_resource_type_for_system(system):
        print(f"system={system}, rt={resource_type}, hosts={config_db.get_hosts_for_system_resource_type(system, resource_type)}")
        for host in config_db.get_hosts_for_system_resource_type(system, resource_type):
            for metric in config_db.get_metrics_for_host_system(system, resource_type, host):
                print(f"gfun_host_{resource_type}_{metric}({system},{host})")



#gfun_host_linux_os_cpu(host)


t = config_db.run_sql_query("SELECT DISTINCT system FROM config")
print(f"{t["system"].tolist()}")

for system in config_db.run_sql_query("SELECT DISTINCT system FROM config")["system"].tolist():
    for resource_type in config_db.run_sql_query("SELECT DISTINCT resource_type FROM config WHERE system='{system}'")["resource_type"].tolist():
        print(f"system={system}, rt={resource_type}, hosts={config_db.get_hosts_for_system_resource_type(system, resource_type)}")
        for host in config_db.get_hosts_for_system_resource_type(system, resource_type):
            for metric in config_db.get_metrics_for_host_system(system, resource_type, host):
                print(f"gfun_host_{resource_type}_{metric}({system},{host})")