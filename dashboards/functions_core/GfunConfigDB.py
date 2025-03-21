import pandas as pd
import pandasql as psql
import json
import logging

class GfunConfigDB:
    """Class to process and query Grafana configuration data."""

    def __init__(self, config):
        """Initialize the class with config and transform it into a DataFrame."""
        self.config = config
        self.df = self._build_dataframe()

    def _build_dataframe(self):
        """Convert the config into a pandas DataFrame."""
        try:
            json_dict = json.loads(self.config.model_dump_json())  # Convert to dictionary
            data_list = []  # Store extracted data
            
            for sys in json_dict.get('systems', []):
                sys_name = sys.get('name', '')
                resource_type = sys.get('resources_types', '')

                for metric in sys.get('config', {}).get('metrics', []):
                    metric_name = metric.get('name', '')

                    for host in sys.get('config', {}).get('ips', []):
                        hostname = self._check_alias(host.get('alias'), host.get('ip'))
                        data_list.append({
                            "system": sys_name,
                            "resource_type": resource_type,
                            "host": hostname,
                            "metric": metric_name
                        })

            return pd.DataFrame(data_list)

        except Exception as err:
            logging.error("Failed to convert data model to DataFrame: %s", err)
            return pd.DataFrame(columns=["system", "resource_type", "host", "metric"])

    @staticmethod
    def _check_alias(alias, ip):
        """Return alias if defined, otherwise return IP."""
        return alias if alias else ip

    def run_sql_query(self, query):
        """Execute an SQL query on the DataFrame, using 'config' as the table name."""
        return psql.sqldf(query, {"config": self.df})  # Use 'config' as the table name

    def get_system_list(self):
        """Return a list of unique systems."""
        return self.df["system"].unique().tolist()

    def get_resource_type_for_system(self, system_name):
        """Return a list of unique hosts for a given system."""
        return self.df[self.df["system"] == system_name]["resource_type"].unique().tolist()

    def get_hosts_for_system_resource_type(self, system_name, resource_type):
        """Return a list of unique hosts for a given system."""
        return self.df[(self.df["system"] == system_name) & (self.df["resource_type"] == resource_type)]["host"].unique().tolist()

    def get_metrics_for_host_system(self, system_name, resource_type, host_name):
        """Return unique metrics for a given system and host."""
        filtered_df = self.df[(self.df["system"] == system_name) & (self.df["resource_type"] == resource_type) & (self.df["host"] == host_name)]
        return filtered_df["metric"].unique().tolist()

    def get_distinct_rows(self):
        """Return distinct rows from the DataFrame."""
        return self.df.drop_duplicates()

