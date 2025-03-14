########################################################################################################################
# PROJECT: observIT dashboards container
# DESCRIPTION: Main dashboards functions
# AUTHOR: machadon
# DATE: 2025-03-13
########################################################################################################################

########################################################################################################################
# IMPORTS
########################################################################################################################

from functions_core.gfun_dm import *
from functions_core.gfun_utils import *
from functions_core.grafanalib_ext import *
from functions import *


########################################################################################################################
#
# function: build_dashboards
#
# This function builds a grafana dashboard based on the monitored items, configured on the config.yaml file.
########################################################################################################################

def gfun_main(config):
    # Dashboards will be overwritten

    logging.debug("%s: Automagically build grafana dashboards", gfun_main.__name__)
    grafana_api_key = config.global_parameters.grafana_api_key
    grafana_server = config.global_parameters.grafana_server + ":3000"

    
    systems = data_model_build(config)

    for sys in systems:
        my_dashboard = gfun_create_system_dashboard(sys, config)
        my_dashboard_json = get_dashboard_json(my_dashboard, overwrite=True, message="Updated by dashboards observit module")
        #logging.debug("Created dashboard %s", my_dashboard_json)
        upload_to_grafana(my_dashboard_json, grafana_server, grafana_api_key)

    hosts_per_res = data_model_get_hosts_per_resource_grouped(systems)
    my_dashboard = gfun_create_home_dashboard(hosts_per_res)
    
    my_dashboard_json = get_dashboard_json(my_dashboard, overwrite=True, message="Updated by grafun-cli")
    res = upload_to_grafana(my_dashboard_json, grafana_server, grafana_api_key)

    if res is not None:
        if res.status_code == 200:
            logging.debug(f"Main observIT dashboard created ({res.status_code} {res.reason})")
            return -1
        else:
            logging.error(f"Unable to create Main observIT dashboard error is: {res.status_code} {res.reason}")
    else:
        logging.error(f"Unexpected error occurred!!!")
        return -1

    return 1



def gfun_create_system_dashboard(sys, config):

    panels = []
    templating = []
    y_pos = 3

    panels = panels + create_title_panel(str(sys['system']))

    for res in sys['resources']:
        # Construct the function name dynamically
        function_name = f"gfun_{res['name']}_system_main"

        logging.debug(f"Will call function name {function_name}")

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
        else:
            logging.error(f"Function name {function_name} is not defined!")

    links_panel = [DashboardLink(
        asDropdown=True,
        type="dashboards",
        title="Menu",
        keepTime=False,
    )]

    my_dashboard = Dashboard(
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
    ).auto_panel_ids()

    return my_dashboard



def gfun_create_home_dashboard(data):
    panels = []
    templating = []
    y_pos = 3

    panels = [Text(
        title="observIT",
        gridPos=GridPos(h=3, w=24, x=0, y=0),
        mode="html",
        content="<h1>Capacity Management</h1>",
    )]

    logging.debug(f"Received host list for the creation of main dashboard : {data} ")

    for resource_type, systems in data.items():
        # Dynamically determine the function to call based on resource type
        #print(f"My data is {resource_type} / {systems} ")

        graph_function_name = f"gfun_{resource_type}_home_main"
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
                        logging.error(f"Function name {function_name} is not defined!")
                        raise ValueError(f"Function '{graph_function_name}' not found.")
                except Exception as e:
                    logging.error(f"Error processing {system}, {host} for {resource_type}: {e}")

    links_panel = [DashboardLink(
        asDropdown=True,
        type="dashboards",
        title="Menu",
        keepTime=False,
    )]

    my_dashboard = Dashboard(
        title="Home observit",
        description="observIT home dashboard",
        tags=["observit"],
        timezone="browser",
        refresh="1m",
        time= Time("now-12M", "now+3M"),
        panels=panels,
        templating=Templating(templating),
        links=links_panel,
    ).auto_panel_ids()
 

    return my_dashboard 



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
