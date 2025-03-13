########################################################################################################################
# PROJECT: observIT dashboards container
# DESCRIPTION: powerstore graphics creation
# AUTHOR: machadon
# DATE: 2025-03-13
########################################################################################################################

########################################################################################################################
# IMPORTS
########################################################################################################################

from functions_core.grafanalib_ext import *

########################################################################################################################
#
# CONSTANT DEFINITION
#
########################################################################################################################


########################################################################################################################
#
# FUNCTIONS: Main Function
#
########################################################################################################################


def gfun_powerstore_main(system_name, resource_name, data, global_pos):

    panels_list = []
    y_pos = global_pos

    for metric in data:
        match metric['metric']:
            case "node":
                y_pos, panel = gfun_powerstore_node_cpu(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
                y_pos, panel = gfun_powerstore_node_read(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
                y_pos, panel = gfun_powerstore_node_write(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
                y_pos, panel = gfun_powerstore_node_total(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
            case "space":
                y_pos, panel = gfun_powerstore_space(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

    return y_pos, panels_list


########################################################################################################################
#
# FUNCTIONS: Plot a graphic for each metric
#
########################################################################################################################

def gfun_powerstore_node_cpu(system_name, resource_name, metric, y_pos):
    str_title = f"CPU Usage ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    panels_target_list_cpu_use = []

    for host in metric['hosts']:
        panels_target_list_cpu_use.append(
            InfluxDBTarget(
                query=f"SELECT 100 * mean(\"io_workload_cpu_utilization\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",      
                alias="$tag_host $tag_node_id"
            )
        )

    # Create Panel to show CPU use Graph
    panels_list.append(CollectorTimeSeries(
        title="CPU utilization (%)",
        dataSource='default',
        targets=panels_target_list_cpu_use,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="percent",
        gridPos=GridPos(h=7, w=24, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="right",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        legendSortDesc=False,
        tooltipMode="multi",
        valueMax=100,
        )
    )

    line = line + 7

    return line, panels_list


def gfun_powerstore_node_read(system_name, resource_name, metric, y_pos):
    str_title = f"Read Performance ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    # Create Panel to show Read Latency
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"avg_read_latency\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Read Latency Avg",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="µs",
        gridPos=GridPos(h=7, w=8, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Create Panel to show Read IO
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"read_iops\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Read IOPS",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="iops",
        gridPos=GridPos(h=7, w=8, x=8, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Create Panel to show Read Bandwidth
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"read_bandwidth\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Read Bandwidth",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="binBps",
        gridPos=GridPos(h=7, w=8, x=16, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    line = line + 7

    return line, panels_list


def gfun_powerstore_node_write(system_name, resource_name, metric, y_pos):
    str_title = f"Write Performance ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    # Create Panel to show Write Latency
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"avg_write_latency\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Write Latency Avg",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="µs",
        gridPos=GridPos(h=7, w=8, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Create Panel to show Write IO
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"write_iops\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Write IOPS",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="iops",
        gridPos=GridPos(h=7, w=8, x=8, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Create Panel to show Write Bandwidth
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"write_bandwidth\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Write Bandwidth",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="binBps",
        gridPos=GridPos(h=7, w=8, x=16, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    line = line + 7

    return line, panels_list



def gfun_powerstore_node_total(system_name, resource_name, metric, y_pos):
    str_title = f"Total Performance ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    # Create Panel to show Write Latency
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"avg_latency\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Total Latency Avg",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="µs",
        gridPos=GridPos(h=7, w=8, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Create Panel to show Total IOPS
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"total_iops\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Total IOPS",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="iops",
        gridPos=GridPos(h=7, w=8, x=8, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Create Panel to show Total Bandwidth
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"total_bandwidth\") FROM \"powerstore_node\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"node_id\"::tag fill(null)",
                alias="$tag_host $tag_node_id"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Total Bandwidth",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="binBps",
        gridPos=GridPos(h=7, w=8, x=16, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    line = line + 7

    return line, panels_list



def gfun_powerstore_space(system_name, resource_name, metric, y_pos):

    # marteladão - tem de ser melhorado (está a forçar este painel a seguir ao cpu)
    y_pos = 4
    str_title = f"Capacity ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    #panels_target_list = []
    panels_target_physical_list = []
    panels_target_reduction_list = []
    panels_target_logical_list = []
    for host in metric['hosts']:
        #Target queries for Physical Space
        panels_target_physical_list.append(
                InfluxDBTarget(
                query=f"SELECT max(\"physical_total\") FROM \"powerstore_space\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"appliance_id\"::tag fill(null)",
                alias="$tag_host $tag_appliance_id Physical Total",
            ),
        )
        panels_target_physical_list.append(
            InfluxDBTarget(
                query=f"SELECT max(\"physical_used\") FROM \"powerstore_space\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"appliance_id\"::tag fill(null)",
                alias="$tag_host $tag_appliance_id Physical Used",
            ),
        )
        # Target queries for Data Reduction
        panels_target_reduction_list.append(
                InfluxDBTarget(
                query="SELECT max(\"data_reduction\") FROM \"powerstore_space\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      "GROUP BY time($__interval), \"host\"::tag, \"appliance_id\"::tag fill(null)",
                alias="$tag_host $tag_appliance_id Data Reduction",
            ),
        )
        #Target queries for Logical Space
        panels_target_logical_list.append(
                InfluxDBTarget(
                query=f"SELECT max(\"logical_provisioned\") FROM \"powerstore_space\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"appliance_id\"::tag fill(null)",
                alias="$tag_host $tag_appliance_id Logical Provisioned",
            ),
        )
        panels_target_logical_list.append(
            InfluxDBTarget(
                query=f"SELECT max(\"logical_used\") FROM \"powerstore_space\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"appliance_id\"::tag fill(null)",
                alias="$tag_host $tag_appliance_id Logical Used",
            ),
        )

        # Panel for Logical Space
    panels_list.append(CollectorTimeSeries(
        title="Space Usage Logical",
        dataSource='default',
        targets=panels_target_logical_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="bytes",
        gridPos=GridPos(h=7, w=8, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Panel for Data Reduction
    panels_list.append(CollectorTimeSeries(
        title="Space Data Reduction",
        dataSource='default',
        targets=panels_target_reduction_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="none",
        valueMax=12,
        valueDecimals=2,
        gridPos=GridPos(h=7, w=8, x=8, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    #Panel for Physical Space
    panels_list.append(CollectorTimeSeries(
        title="Space Usage Physical",
        dataSource='default',
        targets=panels_target_physical_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="bytes",
        gridPos=GridPos(h=7, w=8, x=16, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    line = line + 7

    return line, panels_list
