from pydantic import BaseModel, Field, ValidationError, root_validator, constr
from typing import List, Optional, Union, Literal
import yaml

# Define individual configurations for each system
class GlobalParameters(BaseModel):
    repository: str
    repository_port: int
    repository_protocol: Literal['tcp']
    repository_api_key: str
    loglevel: Literal['NOTSET', 'INFO', 'WARNING', 'DEBUG', 'ERROR', 'CRITICAL']
    logfile: str
    auto_fungraph: bool
    grafana_api_key: str
    grafana_server: str

class IPAddress(BaseModel):
    ip: str
    alias: str
    ip_host_keys: Optional[str] = None
    ip_user: Optional[str] = None
    ip_proxy: Optional[str] = None
    ip_protocol: Optional[Literal['http', 'https']] = None
    ip_pwd64: Optional[str] = None
    ip_unsecured: Optional[bool] = None

class Metric(BaseModel):
    name: str

class ConfigParametersLinux(BaseModel):
    user: str
    host_keys: str
    port: Optional[int] = None
    proxy: Optional[str] = None
    poll: int

class ConfigParametersPowerStor(BaseModel):
    protocol: Literal['http', 'https']
    port: Optional[int] = None
    user: str
    pwd64: str
    unsecured: Optional[bool] = None
    proxy: Optional[str] = None
    poll: int

class ConfigParametersRedfish(BaseModel):
    protocol: Literal['http', 'https']
    port: Optional[int] = None
    user: str
    pwd64: str
    unsecured: Optional[bool] = None
    proxy: Optional[str] = None
    poll: int

class SystemConfig(BaseModel):
    parameters: Union[ConfigParametersLinux, ConfigParametersPowerStor, ConfigParametersRedfish]
    metrics: List[Metric]
    ips: List[IPAddress]

class System(BaseModel):
    name: str
    resources_types: str
    config: SystemConfig

class RootModel(BaseModel):
    systems: List[System]
    global_parameters: GlobalParameters

# Example YAML Data
yaml_data = """
systems:
  - name: demo1
    resources_types: linux_os
    config:
      parameters:
        user: fjcollector
        host_keys: keys/id_rsa
        port: 
        proxy: 
        poll: 1
      metrics:
        - name: cpu
        - name: mem
        - name: fs
        - name: net
      ips:
        - ip: 10.8.1.1
          alias: linux1
        - ip: 10.8.1.2
          alias: linux2
  - name: powerstor1
    resources_types: powerstor
    config:
      parameters:
        protocol: http
        port: 
        user: apereira
        pwd64: TBD
        unsecured: True
        proxy: 
        poll: 1
      metrics:
        - name: node
      ips:
        - ip: 10.10.9.9
          alias: powerstor1
  - name: irmc
    resources_types: redfish
    config:
      parameters:
        protocol: https
        port: 
        user: apereira
        pwd64: TBD
        unsecured: False
        proxy: 
        poll: 1
      metrics:
        - name: power
        - name: temp
      ips:
        - ip: 10.10.10.1
          alias: server1
          ip_protocol: http
global_parameters:
  repository: influxdb
  repository_port: 8086
  repository_protocol: tcp
  repository_api_key: TBD
  loglevel: DEBUG
  logfile: logs/fjcollector.log
  auto_fungraph: True
  grafana_api_key: TBD
  grafana_server: grafana
"""

# Parse YAML into Python dict
data = yaml.safe_load(yaml_data)

# Validate
try:
    validated_data = RootModel(**data)
    print("YAML is valid!")
except ValidationError as e:
    print("Validation errors:", e)




##############################


from pydantic import BaseModel, Field, root_validator, create_model
from typing import List, Optional, Dict, Any
import yaml

# Define the base configuration model
class BaseConfig(BaseModel):
    user: str
    pwd64: str
    unsecured: bool
    proxy: Optional[str] = None
    proxy_user: Optional[str] = None
    proxy_pwd64: Optional[str] = None
    poll: int
    port: Optional[int] = None  # Optional, since it might not exist for all types
    host_keys: Optional[str] = None  # Optional field for linux_os

    @root_validator(pre=True)
    def validate_common_fields(cls, values):
        resources_types = values.get("resources_types")
        if resources_types == "linux_os" and not values.get('host_keys'):
            raise ValueError("host_keys is required for linux_os resource type.")
        return values

# Define dynamic creation of models based on resource type
def create_resource_type_model(resource_type: str):
    """Create a Pydantic model dynamically based on resource type."""
    
    # Define the basic fields for every resource type
    dynamic_fields = {
        "resources_types": (str, resource_type),
        "metrics": (List[Dict[str, str]], []),  # Default empty list for metrics
    }

    # Based on resource type, define additional fields or modify the model
    if resource_type == "powerstore":
        dynamic_fields["protocol"] = (str, "http")  # Example of a powerstore-specific field
        dynamic_fields["ips"] = (List[Dict[str, str]], [])  # Ips section for powerstore
    elif resource_type == "redfish":
        dynamic_fields["url"] = (str, "")  # URL field for redfish
        dynamic_fields["ips"] = (List[Dict[str, str]], [])  # Ips section for redfish
    elif resource_type == "linux_os":
        dynamic_fields["host_keys"] = (str, None)  # Specific to linux_os
        dynamic_fields["ips"] = (List[Dict[str, str]], [])  # Ips section for linux_os
    else:
        dynamic_fields["ips"] = (List[Dict[str, str]], [])  # Default ips section for all types

    # Create and return a Pydantic model dynamically
    return create_model(f"{resource_type.capitalize()}Config", **dynamic_fields)

# Now, generate the system model with dynamic resource-specific configuration
class System(BaseModel):
    name: str
    resources_types: str
    config: BaseConfig
    metrics: List[Dict[str, str]]
    ips: List[Dict[str, str]]

    @root_validator(pre=True)
    def validate_resource_type(cls, values):
        # Dynamically load the correct configuration model for each resource_type
        resource_type = values.get("resources_types")
        config_model = create_resource_type_model(resource_type)

        # Replace config with the dynamically generated class
        values["config"] = config_model(**values["config"])
        return values


class Systems(BaseModel):
    systems: List[System]

# Example YAML input for testing
yaml_input = """
systems:
  - name: powerstor1
    resources_types: powerstore
    config:
      protocol: http
      port: 8080
      user: apereira
      pwd64: TBD
      unsecured: True
      proxy: None
      proxy_user: youknowwho
      proxy_pwd64: TBD
      poll: 1
    metrics:
      - name: node
      - name: vol
    ips:
      - ip: 10.10.9.9
        alias: powerstor1
  - name: redfish1
    resources_types: redfish
    config:
      user: apereira
      pwd64: TBD
      unsecured: True
      proxy: None
      proxy_user: youknowwho
      proxy_pwd64: TBD
      poll: 1
    metrics:
      - name: power
      - name: temperature
    ips:
      - url: http://10.10.10.1:8080
        alias: redfish1
  - name: linuxos1
    resources_types: linux_os
    config:
      user: fjcollector
      host_keys: keys/id_rsa
      port: None
      proxy: None
      poll: 1
    ips:
      - ip: 10.8.1.1
        alias: linux1
      - ip: 10.8.1.2
        alias: linux2
        ip_user: uknowwu
        ip_pwd64: TBD
"""

# Convert YAML to Python (you can use PyYAML to load this)
data = yaml.safe_load(yaml_input)

# Validate with Pydantic
systems = Systems(**data)
print(systems)
