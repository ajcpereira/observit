

import json, requests, logging
from platform import system

from functions_core.yaml_validate import *
from functions_core.grafanafun_dm import *
from functions_core.grafanalib_ext import *
from functions_core.gfun_descriptions import *
from grafanalib._gen import DashboardEncoder

########################################################################################################################
#
# Resource Type: linux_os
#
########################################################################################################################


def graph_linux_os(system_name, resource_name, data, global_pos):
    # todo:

    panels_list = []
    y_pos = global_pos

    for metric in data:
        match metric['metric']:
            case "cpu":
                y_pos, panel = graph_linux_os_cpu(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "mem":
                y_pos, panel = graph_linux_os_mem(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "fs":
                y_pos, panel = graph_linux_os_fs(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "net":
                y_pos, panel = graph_linux_os_net(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

    return y_pos, panels_list


########################################################################################################################
#
# Resource Type: graph_linux_os_cpu
#   Plot
#
########################################################################################################################
def graph_linux_os_cpu(system_name, resource_name, metric, y_pos):
    str_title = f"CPU Usage ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    panels_target_list_cpu_use = []
    panels_target_list_cpu_load = []
    for host in metric['hosts']:
        panels_target_list_cpu_use.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"use\") FROM \"cpu\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag fill(null)",
                alias="$tag_host"
            )
        )

        panels_target_list_cpu_load.append(
            InfluxDBTarget(
                query=f"SELECT mean(\"load5m\") FROM \"cpu\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"host\"::tag fill(null)",
                alias="$tag_host"
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
        gridPos=GridPos(h=7, w=12, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="right",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        legendSortDesc=False,
        tooltipMode="multi",
        valueMax=100,
        description=GRAPH_LINUX_OS_CPU_DESCRIPTION,
        )
    )

    # Create Panel do show CPU Load
    panels_list.append(CollectorTimeSeries(
        title="CPU Average Load (5 min)",
        dataSource='default',
        targets=panels_target_list_cpu_load,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="",
        gridPos=GridPos(h=7, w=12, x=12, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="right",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
        description=GRAPH_LINUX_OS_LOAD_DESCRIPTION,
        )
    )

    line = line + 7

    return line, panels_list


def graph_linux_os_mem(system_name, resource_name, metric, y_pos):
    str_title = f"Memory Usage ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    pos = y_pos + 1
    x_pos = 0

    query_template = (
        "SELECT last(\"{field}\") FROM \"mem\" "
        "WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
        "GROUP BY time($__interval) fill(none) "
    )

    sorted_hosts = sorted(metric['hosts'])

    for host in sorted_hosts:
        target_mem = [
            InfluxDBTarget(query=query_template.format(field="total", system=system_name, host=host), alias="Total"),
            InfluxDBTarget(query=query_template.format(field="used", system=system_name, host=host), alias="Used"),
        ]

        json_overrides = [

        ]

        panels_list.append(CollectorTimeSeries(
            title=f"{host} Memory Usage",
            dataSource='default',
            targets=target_mem,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints='auto',
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=50,
            unit='decmbytes',
            gridPos=GridPos(h=7, w=4, x=x_pos, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendSortBy="Name",
            legendCalcs=['last', 'mean', 'max'],
            valueDecimals=0,
            tooltipMode="multi",
            overrides=json_overrides,
            description=GRAPH_LINUX_OS_MEM_DESCRIPTION,
        )
        )

        x_pos += 4
        if x_pos == 24:
            x_pos = 0
            pos += 7

    pos += 7

    return pos, panels_list


def graph_linux_os_net(system_name, resource_name, metric, y_pos):
    str_title = f"Network Usage ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    pos = y_pos + 1

    for host in metric['hosts']:
        target_net = [
            InfluxDBTarget(
                query=f"SELECT non_negative_derivative(mean(\"tx_bytes\"), 1s)*8 FROM \"net\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}' AND \"if\"::tag!='lo') AND $timeFilter "
                      f"GROUP BY time($__interval), \"if\"::tag fill(null)",
                alias="$tag_if (Tx)"
            ),
            InfluxDBTarget(
                query=f"SELECT non_negative_derivative(mean(\"rx_bytes\"), 1s)*8 FROM \"net\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}' AND \"if\"::tag!='lo') AND $timeFilter "
                      f"GROUP BY time($__interval), \"if\"::tag fill(null)",
                alias="$tag_if (Rx)"
            )
        ]

        override_lst = [
            {
                "matcher": {
                    "id": "byFrameRefID",
                    "options": "B"
                },
                "properties": [
                    {
                        "id": "custom.transform",
                        "value": "negative-Y"
                    }
                ]
            }
        ]

        panels_list.append(CollectorTimeSeries(
            title=host + " Network Traffic",
            dataSource='default',
            targets=target_net,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit=COLLECTOR_NET_UNITS,
            gridPos=GridPos(h=7, w=24, x=0, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="right",
            legendDisplayMode="table",
            stacking={"mode": "normal", "group": "A"},
            legendSortBy="Name",
            legendCalcs=['mean', 'max'],
            legendSortDesc=False,
            tooltipMode="multi",
            overrides=override_lst,
            description=GRAPH_LINUX_OS_NETWORK_DESCRIPTION, 
        ))

        pos = pos + 7

    return pos, panels_list



def graph_linux_os_fs(system_name, resource_name, metric, y_pos):

    str_title = f"File System Capacity ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    pos = y_pos + 1

    for host in metric['hosts']:
        target_fs = [
            InfluxDBTarget(
                query=f"SELECT SUM(\"Total\") FROM (SELECT LAST(\"total\") AS \"Total\" FROM \"fs\" "
                      f"WHERE (\"system\" = '{system_name}' AND \"host\" = '{host}') "
                      f"GROUP BY time($__interval), \"mount\", \"host\", \"system\" fill(null)) WHERE $timeFilter GROUP BY time($__interval)",
                alias="Total"
            ),
            InfluxDBTarget(
                query=f"SELECT SUM(\"Used\") FROM (SELECT LAST(\"used\") AS \"Used\" FROM \"fs\" "
                      f"WHERE (\"system\" = '{system_name}' AND \"host\" = '{host}') "
                      f"GROUP BY time($__interval), \"mount\", \"host\", \"system\" fill(null)) WHERE $timeFilter GROUP BY time($__interval)",
                alias="Used"
            ),
            InfluxDBTarget(
                query=f"SELECT HOLT_WINTERS(SUM(\"Used\"), 30, 0) FROM (SELECT LAST(\"used\") as \"Used\" FROM \"fs\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') "
                      f"GROUP BY time($__interval), \"mount\"::tag, \"host\"::tag, \"system\"::tag fill(null)) "
                      f"WHERE $timeFilter "
                      f"GROUP BY time($__interval)",
                alias="Forecast"
            )
        ]

        target_fs_table = [
            InfluxDBTarget(
                query=f"SELECT \"used\"/\"total\"*100 as \"%Used\", \"total\" as \"Total\", \"used\" as \"Used\", \"total\"-\"used\" as \"Available\" FROM \"fs\" "
                      f"WHERE $timeFilter AND ( \"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') "
                      f"GROUP BY \"mount\"::tag ORDER BY time DESC LIMIT 1",
                format="table"
            )
        ]

        json_overrides = [
            {
                "matcher": {
                    "id": "byName",
                    "options": "Total"
                },
                "properties": [
                    {
                        "id": "custom.fillBelowTo",
                        "value": "Used"
                    },
                    {
                        "id": "color",
                        "value": {
                            "fixedColor": "super-light-blue",
                            "mode": "fixed"
                        }
                    },
                    {
                        "id": "custom.lineWidth",
                        "value": 2
                    }
                ]
            },
            {
                "matcher": {
                    "id": "byName",
                    "options": "Growth"
                },
                "properties": [
                    {
                        "id": "color",
                        "value": {
                            "fixedColor": "orange",
                            "mode": "fixed"
                        }
                    },
                    {
                        "id": "custom.lineWidth",
                        "value": 4
                    },
                    {
                        "id": "custom.axisPlacement",
                        "value": "right"
                    },
                    {
                        "id": "custom.fillOpacity",
                        "value": 0
                    },
                    {
                        "id": "custom.lineInterpolation",
                        "value": "stepAfter"
                    }
                ]
            },
            {
                "matcher": {
                    "id": "byName",
                    "options": "Forecast"
                },
                "properties": [
                    {
                        "id": "color",
                        "value": {
                            "fixedColor": "super-light-purple",
                            "mode": "fixed"
                        }
                    }
                ]
            },
            {
                "matcher": {
                    "id": "byName",
                    "options": "Used"
                },
                "properties": [
                    {
                        "id": "color",
                        "value": {
                            "mode": "fixed",
                            "fixedColor": "blue"
                        }
                    }
                ]
            }
        ]


        panels_list.append(CollectorTimeSeries(
            title=f"{host} Filesystem Usage (Last value interval $__interval)",
            dataSource='default',
            targets=target_fs,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit=COLLECTOR_FS_UNITS,
            gridPos=GridPos(h=10, w=24, x=0, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendCalcs=['mean', 'min', 'max'],
            tooltipMode="multi",
            overrides=json_overrides,
            description=GRAPH_LINUX_OS_FS_DESCRIPTION,
        ))


        json_overrides_table = [
            {
                "matcher": {
                    "id": "byName",
                    "options": "%Used"
                },
                "properties": [
                    {
                        "id": "unit",
                        "value": "percent"
                    },
                    {
                        "id": "custom.cellOptions",
                        "value": {
                            "mode": "basic",
                            "type": "gauge",
                            "valueDisplayMode": "color"
                        }
                    },
                    {
                        "id": "max",
                        "value": 100
                    },
                    {
                        "id": "min",
                        "value": 0
                    },
                    {
                        "id": "thresholds",
                        "value": {
                            "mode": "percentage",
                            "steps": [
                                {
                                    "color": "green",
                                    "value": None
                                },
                                {
                                    "color": "red",
                                    "value": 95
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "matcher": {
                    "id": "byName",
                    "options": "Time"
                },
                "properties": [
                    {
                        "id": "custom.hidden",
                        "value": True
                    }
                ]
            }
        ]

        table_field_sort = [TableSortByField(displayName='%Used', desc=True)]

        panels_list.append(CollectorTable(
            title=host + " File System Capacity Table",
            dataSource='default',
            targets=target_fs_table,
            gridPos=GridPos(h=10, w=24, x=0, y=pos + 10),
            filterable=True,
            unit=COLLECTOR_FS_UNITS,
            displayMode="color-text",
            colorMode="thresholds",
            overrides=json_overrides_table,
            sortBy=table_field_sort,
            )
        )

        pos = pos + 20

    return pos, panels_list

