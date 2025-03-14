########################################################################################################################
# PROJECT: observIT dashboards container
# DESCRIPTION: eternus_dx graphics creation
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

def gfun_eternus_dx_main(system_name, resource_name, data, global_pos):

    panels_list = []
    y_pos = global_pos

    for metric in data:
        match metric['metric']:
            case "cpu":
                y_pos, panel = gfun_eternus_dx_cpu(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
            case "tppool":
                y_pos, panel = gfun_eternus_dx_tpp(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
            case "vol":
                 y_pos, panel = gfun_eternus_dx_vol_read(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
                 y_pos, panel = gfun_eternus_dx_vol_write(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
            case "power":
                 y_pos, panel = gfun_eternus_dx_power(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
            case "temp":
                 y_pos, panel = gfun_eternus_dx_temp(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
            #case _:
            #    print("no option was found!!!")

    return y_pos, panels_list


########################################################################################################################
#
# FUNCTIONS: Plot a graphic for each metric
#
########################################################################################################################


def gfun_eternus_dx_cpu(system_name, resource_name, metric, y_pos):
    str_title = f"CPU Usage ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    panels_target_list_cpu_use = []

    for host in metric['hosts']:
        panels_target_list_cpu_use.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"busyrate\") FROM \"eternus_dx_cpu\" " 
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"CM\"::tag, \"Core\"::tag fill(null)",
                alias="$tag_host CM#$tag_CM Core#$tag_Core"
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




def gfun_eternus_dx_vol_read(system_name, resource_name, metric, y_pos):
    str_title = f"Read Performance ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    # Create Panel to show Read Latency
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"read_avg_time\") FROM \"eternus_dx_vol\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"vol_id\"::tag fill(null)",
                alias="$tag_host $tag_vol_id"
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
        unit="ms",
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
                query=f"SELECT mean(\"read_iops\") FROM \"eternus_dx_vol\" "
                f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                f"GROUP BY time($__interval), \"host\"::tag, \"vol_id\"::tag fill(null)",
                alias="$tag_host $tag_vol_id"
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
                query=f"SELECT mean(\"read_throughput\") FROM \"eternus_dx_vol\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"vol_id\"::tag fill(null)",
                alias="$tag_host $tag_vol_id"
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
        unit="MBs",
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


def gfun_eternus_dx_vol_write(system_name, resource_name, metric, y_pos):
    str_title = f"Write Performance ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    # Create Panel to show Write Latency
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"write_avg_time\") FROM \"eternus_dx_vol\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter " 
                      f"GROUP BY time($__interval), \"host\"::tag, \"vol_id\"::tag fill(null)",
                alias="$tag_host $tag_vol_id"
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
        unit="ms",
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
                query=f"SELECT mean(\"write_iops\") FROM \"eternus_dx_vol\" "
                f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                f"GROUP BY time($__interval), \"host\"::tag, \"vol_id\"::tag fill(null)",
                alias="$tag_host $tag_vol_id"
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
                query=f"SELECT mean(\"write_throughput\") FROM \"eternus_dx_vol\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag, \"vol_id\"::tag fill(null)",
                alias="$tag_host $tag_vol_id"
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
        unit="MBs",
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


def gfun_eternus_dx_power(system_name, resource_name, metric, y_pos):
    str_title = f"Power Consumption ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    # Create Panel to Power Consumption
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"power_watt\") FROM \"eternus_dx_power\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag fill(null)",
                alias="$tag_host"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Power Consumption",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="watt",
        gridPos=GridPos(h=7, w=12, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    # Create Panel to show CO2 emissions
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT 0.00085 * mean(\"power_watt\") FROM \"eternus_dx_power\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag fill(null)",
                alias="$tag_host"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="CO2 Emissions",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="masskg",
        gridPos=GridPos(h=7, w=12, x=12, y=line),
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

def gfun_eternus_dx_temp(system_name, resource_name, metric, y_pos):
    str_title = f"Intake Temperature ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    # Create Panel to Intake Temperature
    panels_target_list = []
    for host in metric['hosts']:
        panels_target_list.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"intake_temp\") FROM \"eternus_dx_temp\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag fill(null)",
                alias="$tag_host"
            )
        )

    panels_list.append(CollectorTimeSeries(
        title="Intake Temperature",
        dataSource='default',
        targets=panels_target_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="celsius",
        gridPos=GridPos(h=7, w=24, x=0, y=line),
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


def gfun_eternus_dx_dashboard_vars(system, data):
    tpl_lst = []

    for metric in data:
        host = metric['hosts'][0]
        match metric['metric']:
            case "tppool":
                tpl_lst = tpl_lst + [Template(
                    # dataSource="default",
                    name='tpp',
                    label='tpp',
                    query=f"SHOW TAG VALUES WITH KEY = \"tppool_nr\" WHERE \"system\"::tag = '{system}'",
                    type='query',
                    includeAll=True,
                    multi=True,
                    allValue="",
                    default='All',
                    refresh=2,
                    hide=HIDE_VARIABLE,
                )
                ]

    return tpl_lst



def gfun_eternus_dx_tpp(system_name, resource_name, metric, y_pos):

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
                query=f"SELECT max(\"total_capacity\") FROM \"eternus_dx_tppool\" "
                f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}' AND \"tppool_nr\"::tag =~ /^$tpp$/) AND $timeFilter "
                f"GROUP BY time($__interval), \"host\"::tag, \"tppool_nr\"::tag fill(null)",
                alias="$tag_host TPP#$tag_tppool_nr Physical Capacity",
            ),
        )
        panels_target_physical_list.append(
                InfluxDBTarget(
                query=f"SELECT max(\"use_capacity\") FROM \"eternus_dx_tppool\" "
                f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}' AND \"tppool_nr\"::tag =~ /^$tpp$/) AND $timeFilter "
                f"GROUP BY time($__interval), \"host\"::tag, \"tppool_nr\"::tag fill(null)",
                alias="$tag_host TPP#$tag_tppool_nr Physical Used",
            ),
        )
        panels_target_physical_list.append(
                InfluxDBTarget(
                query=f"SELECT max(\"total_size_requested\") FROM \"eternus_dx_tppool\" "
                f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}' AND \"tppool_nr\"::tag =~ /^$tpp$/) AND $timeFilter "
                f"GROUP BY time($__interval), \"host\"::tag, \"tppool_nr\"::tag fill(null)",
                alias="$tag_host TPP#$tag_tppool_nr Logical Requested",
            ),
        )


        # Panel for Logical Space
    panels_list.append(CollectorTimeSeries(
        title="Space Usage Physical per TPP",
        repeat=Repeat(direction='h', variable='tpp', maxPerRow=2),
        dataSource='default',
        targets=panels_target_physical_list,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="decmbytes",
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

    line = line + 7

    return line, panels_list

def graph_eternus_dx_dashboard_vars(system, data):
    tpl_lst = []

    for metric in data:
        host = metric['hosts'][0]
        match metric['metric']:
            case "tppool":
                tpl_lst = tpl_lst + [Template(
                    # dataSource="default",
                    name='tpp',
                    label='tpp',
                    query=f"SHOW TAG VALUES WITH KEY = \"tppool_nr\" WHERE \"system\"::tag = '{system}'",
                    type='query',
                    includeAll=True,
                    multi=True,
                    allValue="",
                    default='All',
                    refresh=2,
                    hide=HIDE_VARIABLE,
                )
                ]

    return tpl_lst


