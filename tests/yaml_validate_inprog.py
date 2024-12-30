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
    
#####################
    
from pydantic import BaseModel, root_validator, ValidationError, validator, create_model
from typing import List, Dict, Optional, Any
import yaml

# Define validation rules for each resource_type
RESOURCE_TYPE_VALIDATIONS = {
    "linux_os": {
        "metrics": ["cpu", "mem", "fs", "net"],
        "required_parameters": ["user", "host_keys", "port"],  # Example of required parameters for linux_os
    },
    "powerstor": {
        "metrics": ["node", "disk"],
        "required_parameters": ["protocol", "port", "user", "pwd64"],
    },
    "redfish": {
        "metrics": ["power", "temp"],
        "required_parameters": ["protocol", "user", "pwd64", "unsecured"],
    },
}

# Helper function to create a dynamic model for each resource_type
def create_dynamic_resource_model(resource_type: str) -> BaseModel:
    """Create a dynamic model based on resource_types with validation."""
    # Check the validation schema for the resource_type
    validation = RESOURCE_TYPE_VALIDATIONS.get(resource_type, {})

    # Create the model with metrics and parameters that follow the defined schema
    return create_model(
        f"{resource_type.capitalize()}Config",
        parameters=Dict[str, Optional[str]],
        metrics=List[str],
        ips=List[Dict[str, str]],
        # Custom validation function (validated at the root level)
        _validate_metrics=True,
        __validators__=validation,
    )

# Dynamic system configuration model with validation logic
class DynamicSystemConfig(BaseModel):
    name: str
    resources_types: str
    config: Any

    # Root-level validator to validate metrics and parameters based on resource_types
    @root_validator(pre=True)
    def validate_resource_type_fields(cls, values):
        resource_type = values.get('resources_types')
        config = values.get('config', {})

        # Get the validation rules for the given resource_type
        validation = RESOURCE_TYPE_VALIDATIONS.get(resource_type)

        if not validation:
            raise ValueError(f"Unknown resource type: {resource_type}")

        # Validate metrics
        metrics = config.get('metrics', [])
        valid_metrics = validation.get("metrics", [])
        invalid_metrics = [metric for metric in metrics if metric not in valid_metrics]

        if invalid_metrics:
            raise ValueError(f"Invalid metrics for '{resource_type}': {', '.join(invalid_metrics)}")

        # Validate required parameters
        required_params = validation.get("required_parameters", [])
        missing_params = [param for param in required_params if param not in config.get('parameters', {})]
        if missing_params:
            raise ValueError(f"Missing required parameters for '{resource_type}': {', '.join(missing_params)}")

        return values


# Function to build dynamic models for each resource type and validate data
def build_dynamic_models(data: Dict[str, Any]) -> Dict[str, BaseModel]:
    """Build dynamic models based on resource_types in the YAML."""
    models = {}

    for item in data.get("systems", []):
        resource_type = item.get("resources_types", "")
        
        if resource_type:
            # Generate the model dynamically based on resource_type
            config_model = create_dynamic_resource_model(resource_type)
            
            # Create a dynamic model for each system
            models[item["name"]] = DynamicSystemConfig

    return models


# Function to load and validate YAML content dynamically using generated models
def load_and_validate_yaml(yaml_content: str):
    # Parse the YAML content into a Python dict
    data = yaml.safe_load(yaml_content)
    
    # Build dynamic models for the systems based on the resource_types
    models = build_dynamic_models(data)

    # Validate each system using the generated model
    for system in data.get("systems", []):
        resource_name = system["name"]
        system_model = models.get(resource_name)

        if system_model:
            try:
                # Validate the system using its respective dynamic model
                system_instance = system_model(**system)
                print(f"Validated system: {system_instance.json(indent=2)}")
            except ValidationError as e:
                print(f"Validation failed for {resource_name}: {e}")


# Example YAML input (as a string)
yaml_content = """
systems:
  - name: demo1
    resources_types: linux_os
    config:
      parameters:
        user: fjcollector
        host_keys: keys/id_rsa
        port: 22
      metrics:
        - cpu
        - mem
        - fs
        - net
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
        port: 8080
        user: apereira
        pwd64: TBD
      metrics:
        - node
      ips:
        - ip: 10.10.9.9
          alias: powerstor1
  - name: irmc
    resources_types: redfish
    config:
      parameters:
        protocol: https
        user: apereira
        pwd64: TBD
        unsecured: False
      metrics:
        - power
        - temp
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

# Load and validate the YAML content
load_and_validate_yaml(yaml_content)
