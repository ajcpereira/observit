from pydantic import BaseModel, ValidationError, model_validator, field_validator
from typing import List, Dict, Union, Optional, Any
import yaml

# Define validation rules for each resource_type
RESOURCE_TYPE_VALIDATIONS = {
    "linux_os": {
        "metrics": ["cpu", "mem", "fs", "net"],
        "required_parameters": ["user", "host_keys", "port"],
        "optional_parameters": ["custom_script"],
    },
    "powerstor": {
        "metrics": ["node", "disk"],
        "required_parameters": ["protocol", "port", "user", "pwd64"],
        "optional_parameters": ["snmp_community"],
    },
    "redfish": {
        "metrics": ["power", "temp"],
        "required_parameters": ["protocol", "user", "pwd64"],
        "optional_parameters": ["unsecured", "api_version"],
    },
}

# Helper function to create a dynamic model for each resource_type
def create_dynamic_resource_model(resource_type: str) -> BaseModel:
    """Create a dynamic model based on resource_types with validation."""
    validation = RESOURCE_TYPE_VALIDATIONS.get(resource_type, {})

    class DynamicConfig(BaseModel):
        parameters: Dict[str, Union[str, int, bool, None]]
        metrics: List[str]
        ips: List[Dict[str, Optional[str]]]

        @field_validator("metrics", mode="before")
        @classmethod
        def validate_metrics(cls, metrics):
            valid_metrics = validation.get("metrics", [])
            invalid_metrics = [metric for metric in metrics if metric not in valid_metrics]
            if invalid_metrics:
                raise ValueError(f"Invalid metrics: {', '.join(invalid_metrics)}")
            return metrics

        @field_validator("parameters", mode="before")
        @classmethod
        def validate_parameters(cls, parameters):
            required_params = validation.get("required_parameters", [])
            optional_params = validation.get("optional_parameters", [])
            allowed_params = set(required_params + optional_params)

            # Check for missing required parameters
            missing_params = [param for param in required_params if param not in parameters]
            if missing_params:
                raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

            # Coerce parameter types to strings where necessary
            for key, value in parameters.items():
                if key in allowed_params and value is not None:
                    parameters[key] = str(value)  # Convert all parameter values to strings

            return parameters

        @field_validator("ips", mode="before")
        @classmethod
        def validate_ips(cls, ips):
            for ip_entry in ips:
                if "ip" not in ip_entry:
                    raise ValueError("Each `ips` entry must have an `ip` field.")
                if "alias" in ip_entry and not isinstance(ip_entry["alias"], str):
                    raise ValueError("`alias` must be a string if provided.")
            return ips

    return DynamicConfig

# Dynamic system configuration model with validation logic
class DynamicSystemConfig(BaseModel):
    name: str
    resources_types: str
    config: Dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def validate_resource_type(cls, values):
        resource_type = values.get("resources_types")
        if resource_type not in RESOURCE_TYPE_VALIDATIONS:
            raise ValueError(f"Unknown resource type: {resource_type}")
        return values

# Function to build dynamic models for each resource type and validate data
def build_dynamic_models(data: Dict[str, Any]) -> Dict[str, DynamicSystemConfig]:
    """Build dynamic models based on resource_types in the YAML."""
    models = {}
    for system in data.get("systems", []):
        resource_type = system.get("resources_types")
        if resource_type:
            dynamic_model = create_dynamic_resource_model(resource_type)
            try:
                # Validate the configuration and dump the validated data
                config_instance = dynamic_model.model_validate(system.get("config", {}))
                validated_config = config_instance.model_dump()

                # Include the validated configuration in the model
                models[system["name"]] = DynamicSystemConfig(
                    name=system["name"],
                    resources_types=resource_type,
                    config=validated_config,
                )
            except ValidationError as e:
                print(f"Validation failed for {system['name']}: {e}")
    return models

# Function to load and validate YAML content dynamically using generated models
def load_and_validate_yaml(yaml_content: str):
    # Parse the YAML content into a Python dict
    data = yaml.safe_load(yaml_content)

    # Build dynamic models for the systems based on the resource_types
    models = build_dynamic_models(data)

    # Output the validated models
    for system_name, model_instance in models.items():
        print(f"Validated system {system_name}: {model_instance.model_dump_json(indent=2)}")

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
        custom_script: startup.sh
      metrics:
        - cpu
        - mem
        - fs
        - net
      ips:
        - ip: 10.8.1.1
          alias: linux1
        - ip: 10.8.1.2
  - name: powerstor1
    resources_types: powerstor
    config:
      parameters:
        protocol: http
        port: 8080
        user: apereira
        pwd64: TBD
        snmp_community: public
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
        api_version: v1.6
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
