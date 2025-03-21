########################################################################################################################
# PROJECT: observIT dashboards container
# DESCRIPTION: Main dashboards functions
# AUTHOR: machadon
# DATE: 2025-03-20
########################################################################################################################

########################################################################################################################
# IMPORTS
########################################################################################################################

import json, pandas
from functions_core.gfun_dm import *
#from functions_core.gfun_config_db import *
from functions_core.GfunConfigDB import *
from functions_core.gfun_utils import *
from functions_core.grafanalib_ext import *
from functions import *


########################################################################################################################
#
# CONSTANT DEFINITION
#
########################################################################################################################

DASHBOARD_CLASS = ["sys", "home"]


########################################################################################################################
#
# function: build_dashboards
#
# This function builds a grafana dashboard based on the monitored items, configured on the config.yaml file.
########################################################################################################################

def gfun_main(config):
    # Dashboards will be overwritten

    logging.info(f"Starting to automagically build observit dashboards")
    grafana_api_key = config.global_parameters.grafana_api_key
    grafana_server = config.global_parameters.grafana_server + ":3000"

    config_db = GfunConfigDB(config)
    #gfun_host_create_dashboard(config_db)

    systems = data_model_build(config)

    for dash_class in DASHBOARD_CLASS:
              # Construct the function name dynamically
        function_name = f"gfun_{dash_class}_create_dashboard"

        logging.debug(f"Will call function name {function_name}()")

        # Get the function from the current module
        function = globals().get(function_name)

        if function:
            sys_dashboards = function(systems, config_db)
            
            for sys_dash in sys_dashboards:
                my_dashboard_json = get_dashboard_json(sys_dash, overwrite=True, message="Updated by dashboards observit module")
                #Insert here some logging identifieng the dashboad name
                logging.info(f"Created dashboard ")
                upload_to_grafana(my_dashboard_json, grafana_server, grafana_api_key)
        else:
            logging.error(f"Function name {function_name} is not defined!")


def gfun_sys_create_dashboard(systems, config_db):

    my_dashboards = []
    #systems = data_model_build(config)

    for sys in systems:
        
        panels = []
        templating = []
        y_pos = 3

        panels = panels + create_title_panel(str(sys['system']))

        for res in sys['resources']:
            # Construct the function name dynamically
            function_name = f"gfun_sys_{res['name']}_main"

            logging.debug(f"Will call function name {function_name}({str(sys['system'])})")

            # Get the function from the current module
            function = globals().get(function_name)

            if function:
                y_pos, res_panel = function(str(sys['system']), str(res['name']), res['data'], y_pos)
                panels = panels + res_panel

                # Handle templating for specific resources
                if res['name'] in ["eternus_cs8000", "eternus_dx"]:
                    templating_function_name = f"graph_{res['name']}_dashboard_vars"
                    templating_function = globals().get(templating_function_name)
                    if templating_function:
                        templating = templating_function(res['data'])


                links_panel = [DashboardLink(
                                asDropdown=True,
                                type="dashboards",
                                title="Menu",
                                keepTime=False,
                                )]

                # Build a list with grafana dashboards
                my_dashboards = my_dashboards + [Dashboard(
                    title="System " + sys['system'] + " dashboard",
                    description="observit auto generated dashboard",
                    tags=[
                        sys['system'], "observit",
                    ],
                    timezone="browser",
                    refresh="1m",
                    panels=panels,
                    templating=Templating(templating),
                    links=links_panel,
                ).auto_panel_ids()]

            else:
                logging.error(f"Function name {function_name} is not defined!")

    return my_dashboards


def gfun_home_create_dashboard(systems, config_db):
    panels = []
    templating = []
    y_pos = 3

    panels = [Text(
        title="observIT",
        gridPos=GridPos(h=3, w=24, x=0, y=0),
        mode="html",
        content="<h1>Capacity Management</h1>",
    )]

    hosts_per_res = data_model_get_hosts_per_resource_grouped(systems)

    logging.debug(f"Received host list for the creation of main dashboard : {hosts_per_res} ")

 
    for resource_type, systems in hosts_per_res.items():
        # Dynamically determine the function to call based on resource type
        #print(f"My data is {resource_type} / {systems} ")

        graph_function_name = f"gfun_home_{resource_type}_main"
        logging.debug(f"I Will call {graph_function_name} ")   
        
        panels.append(RowPanel(title=f"Storage Capacity {resource_type}  ", gridPos=GridPos(h=1, w=24, x=0, y=y_pos)))

        for system, hosts in systems.items():

            logging.debug(f"Calling function {graph_function_name}({system})")
            for host in hosts:
                try:
                    graph_function = globals().get(graph_function_name)
                    if graph_function:
                        y_pos, panel = graph_function(system, host, y_pos)
                        panels = panels + panel
                    else:
                        logging.error(f"Function name {graph_function_name} is not defined!")
                        raise ValueError(f"Function '{graph_function_name}' not found.")
                except Exception as e:
                    logging.error(f"Error processing {system}, {host} for {resource_type}: {e}")

    links_panel = [DashboardLink(
        asDropdown=True,
        type="dashboards",
        title="Menu",
        keepTime=False,
    )]

    my_dashboard = [Dashboard(
        title="Home observit",
        description="observIT home dashboard",
        tags=["observit"],
        timezone="browser",
        refresh="1m",
        time= Time("now-12M", "now+3M"),
        panels=panels,
        templating=Templating(templating),
        links=links_panel,
    ).auto_panel_ids()]
 

    return my_dashboard 


# def gfun_host_create_dashboard(systems, config_db):
#     '''Will return a list of dashboards, one for each host'''

#     my_dashboards = []
#     #systems = data_model_build(config)

#     query = config_db.run_sql_query("SELECT DISTINCT system, resource_type, host FROM config ORDER BY system, resource_type, host")

#     for index, row in query.iterrows():
    
#         panels = []
#         templating = []
#         y_pos = 3

#         panels = panels + create_title_panel("host " + row["host"])

#         # Construct the function name dynamically
#         function_name = f"gfun_host_{row['resource_type']}_main"

#         logging.debug(f"Will call function name {function_name}({row["system"]})")

#         # Get the function from the current module
#         function = globals().get(function_name)

#         if function:
#             y_pos, res_panel = function(row["system"], row["host"], config_db, y_pos)
#             panels = panels + res_panel

#             links_panel = [DashboardLink(
#                             asDropdown=True,
#                             type="dashboards",
#                             title="Menu",
#                             keepTime=False,
#                             )]

#             # Build a list with grafana dashboards
#             my_dashboards = my_dashboards + [Dashboard(
#                 title=f"Host {row["host"]} (System {row["system"]})",
#                 description="observit auto generated dashboard",
#                 tags=[
#                     row["host"], row["system"], "observit",
#                 ],
#                 timezone="browser",
#                 refresh="1m",
#                 panels=panels,
#                 templating=Templating(templating),
#                 links=links_panel,
#             ).auto_panel_ids()]
#         else:
#             logging.error(f"Function name {function_name} is not defined!")

#     return my_dashboards


# def gfun_host_linux_os_main(system, host, config_db, global_pos):
#     '''Will return metric panels'''

#     panels_list = []
#     y_pos = global_pos

#     query = config_db.run_sql_query(f"SELECT DISTINCT metric FROM config WHERE system='{system}' AND resource_type='linux_os' AND host='{host}'")

#     for index, row in query.iterrows():
        
#          # Construct the function name dynamically
#         function_name = f"gfun_host_linux_os_{row['metric']}"
#         logging.debug(f"Will call function name {function_name}({row["system"]}, {row["host"]})")

#         # Get the function from the current module
#         function = globals().get(function_name)

#         if function:
#             y_pos, res_panel = function(system, host, y_pos)
#             panels_list = panels_list + res_panel
#         else:
#             logging.error(f"Function name {function_name} is not defined!")

#     return y_pos, panels_list

# def gfun_host_eternus_cs8000_main(system, host, config_db, global_pos):
#     return gfun_host_linux_os_main(system, host, config_db, global_pos)


########################################################################################################################
#
# Resource Type: create_title_panel
#
########################################################################################################################
def create_title_panel(system_name, panel_title=""):
    str_msg = "<br><p style=\"text-align:center\"><span style=\"font-size:36px\">System " + system_name + "</span></p>"

    panel = [Text(
        title=panel_title,
        gridPos=GridPos(h=3, w=24, x=0, y=0),
        mode="html",
        content=str_msg,
    )]

    return panel
