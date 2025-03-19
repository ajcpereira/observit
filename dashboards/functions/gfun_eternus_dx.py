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

def gfun_sys_eternus_dx_main(system_name, resource_name, data, global_pos):

    panels_list = []
    y_pos = global_pos

    for metric in data:
        match metric['metric']:
            case "cpu":
                y_pos, panel = gfun_sys_eternus_dx_cpu(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
            case "tppool":
                y_pos, panel = gfun_sys_eternus_dx_tpp(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel
            case "vol":
                 y_pos, panel = gfun_sys_eternus_dx_vol_read(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
                 y_pos, panel = gfun_sys_eternus_dx_vol_write(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
            case "power":
                 y_pos, panel = gfun_sys_eternus_dx_power(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
            case "temp":
                 y_pos, panel = gfun_sys_eternus_dx_temp(system_name, resource_name, metric, y_pos)
                 panels_list = panels_list + panel
            #case _:
            #    print("no option was found!!!")

    return y_pos, panels_list


def gfun_home_eternus_dx_main(system, host, y_pos):


    panels_list =[]
    pos = y_pos + 1


   #Define queries
   ############################################################################################################################################
 
   #Query for [storage name] Capacity 
    target_fs = [
        InfluxDBTarget(
            query=f"SELECT SUM(*) FROM (SELECT LAST(\"total_capacity\") FROM \"eternus_dx_tppool\" " 
                    f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
                    f"GROUP BY time($__interval), \"tppool_nr\"::tag fill(null)) WHERE $timeFilter GROUP BY time($__interval)",
            alias="Total"
        ),
        InfluxDBTarget(
            query=f"SELECT SUM(*) FROM (SELECT LAST(\"use_capacity\") FROM \"eternus_dx_tppool\" "
                    f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
                    f"GROUP BY time($__interval), \"tppool_nr\"::tag fill(null)) WHERE $timeFilter GROUP BY time($__interval)",
            alias="Used"
        ),
        InfluxDBTarget(
            query=f"SELECT HOLT_WINTERS(SUM(*), 90, 0) FROM (SELECT LAST(\"use_capacity\") FROM \"eternus_dx_tppool\" "
                    f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
                    f"GROUP BY time($__interval), \"tppool_nr\"::tag fill(null)) WHERE $timeFilter GROUP BY time($__interval)",
            alias="Forecast"
        ),
    ]  

    target_fs.append(
        {
            "refId": "D",
            "datasource": {
                "type": "__expr__",
                "uid": "__expr__",
                "name": "Expression"
            },
            "type": "math",
            "hide": False,
            "expression": "$A*0.8"
         }
      )


    json_overrides_for_capacity = [
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
        },
        {
        "matcher": {
          "id": "byName",
          "options": "D"
        },
        "properties": [
          {
            "id": "custom.lineWidth",
            "value": 5
          },
          {
            "id": "custom.lineStyle",
            "value": {
              "dash": [
                10,
                10
              ],
              "fill": "dash"
            }
          },
          {
            "id": "color",
            "value": {
              "fixedColor": "red",
              "mode": "fixed"
            }
          },
          {
            "id": "custom.fillOpacity",
            "value": 0
          },
          {
            "id": "displayName",
            "value": "80%"
          }
        ]
      }
    ]

    panels_list.append(CollectorTimeSeries(
        title=f"{host} Capacity",
        dataSource='default',
        targets=target_fs,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="decmbytes",
        gridPos=GridPos(h=14, w=9, x=0, y=pos),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendCalcs=['mean', 'min', 'max'],
        tooltipMode="multi",
        overrides=json_overrides_for_capacity,
        valueMin=0,
    ))

    ############################################################################################################################################
    #Query for [storage name] CPU utilization (%) 
    target = [
        InfluxDBTarget(
            query=f"SELECT mean(\"busyrate\") FROM \"eternus_dx_cpu\" "
                f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
                f"GROUP BY time($__interval), \"CM\"::tag fill(null)",
            alias="CM#$tag_CM"
        ),
    ]

    panels_list.append(CollectorTimeSeries(
        title=f"{host} CPU Utilization (%)",
        dataSource='default',
        targets=target,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="percent",
        gridPos=GridPos(h=7, w=4, x=9, y=y_pos),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        legendSortDesc=False,
        tooltipMode="multi",
        valueMax=100,
        )
    )


    ############################################################################################################################################
    #Query: [storage name] IOPS R+W Avg $__interval


    target = [
        InfluxDBTarget(
            query=f"SELECT mean(\"read_iops\")+mean(\"write_iops\") FROM \"eternus_dx_vol\" "
                f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
                f"GROUP BY time($__interval) fill(null)",
            alias="Total IOPS"
        ),
    ]


    panels_list.append(CollectorTimeSeries(
            title=f"{host} Total IOPS",
            dataSource='default',
            targets=target,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit="iops",
            gridPos=GridPos(h=7, w=4, x=9, y=y_pos+7),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendSortBy="Name",
            legendCalcs=['mean', 'max'],
            tooltipMode="multi",
            legendSortDesc=False,
        )
        )

    ############################################################################################################################################
    #Query: [storage name] IOPS R+W Avg $__interval

    target = [
        InfluxDBTarget(
            query=f"SELECT mean(\"read_avg_time\")+mean(\"write_avg_time\") FROM \"eternus_dx_vol\" "
                    f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
                    f"GROUP BY time($__interval) fill(null)",
            alias="Total Latency"
        ),
    ]

    panels_list.append(CollectorTimeSeries(
        title=f"{host} Total Latency",
        dataSource='default',
        targets=target,
        drawStyle='line',
        lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
        showPoints=COLLECTOR_SHOW_POINTS,
        gradientMode=COLLECTOR_GRADIENT_MODE,
        fillOpacity=COLLECTOR_FILL_OPACITY,
        unit="ms",
        gridPos=GridPos(h=7, w=4, x=13, y=y_pos),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement="bottom",
        legendDisplayMode="table",
        legendSortBy="Name",
        legendCalcs=['mean', 'max'],
        tooltipMode="multi",
        legendSortDesc=False,
    )
    )

    ############################################################################################################################################
    #Query: [storage name] Total Throughput R+W Avg $__interval

    target = [
            InfluxDBTarget(
                query=f"SELECT mean(\"read_throughput\")+mean(\"write_throughput\") FROM \"eternus_dx_vol\" "
                        f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag ='{host}' ) AND $timeFilter "
                        f"GROUP BY time($__interval) fill(null)",
                   alias="Total Throughput"
            ),
        ]



    panels_list.append(CollectorTimeSeries(
            title=f"{host} Total Bandwidth",
            dataSource='default',
            targets=target,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit="MBs",
            gridPos=GridPos(h=7, w=4, x=13, y=y_pos+7),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendSortBy="Name",
            legendCalcs=['mean', 'max'],
            tooltipMode="multi",
            legendSortDesc=False,
        )
        )


    ############################################################################################################################################
     # Query for: StorageIO - Volumes with less than 10000 I/O's during the 2 Months
    target = [
        InfluxDBTarget(
            query=f"SELECT sum(\"read_iops\") + sum(\"write_iops\") AS \"Total I/Os\", max(\"vol_size\") as \"Volume Capacity\" FROM \"eternus_dx_vol\" "
                    f"WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') AND $timeFilter "
                    f"GROUP BY \"host\"::tag, \"vol_id\"::tag fill(none)",
            format="table"
        )
    ]


    json_overrides_table = [
        {
            "matcher": {
            "id": "byName",
            "options": "Volume Capacity"
            },
            "properties": [
            {
                "id": "unit",
                "value": "mbytes"
            }
            ]
        },
        {
            "matcher": {
            "id": "byName",
            "options": "vol_id"
            },
            "properties": [
            {
                "id": "unit"
            },
            {
                "id": "custom.width",
                "value": 107
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

    transformation = [
    {
      "id": "filterByValue",
      "options": {
        "filters": [
          {
            "config": {
              "id": "lower",
              "options": {
                "value": 10000
              }
            },
            "fieldName": "Total I/Os"
          }
        ],
        "match": "all",
        "type": "include"
      }
    }
  ]


    table_field_sort = [TableSortByField(displayName='Total I/O', desc=True)]

    panels_list.append(CollectorTable(
        title=f"{host} StorageIO - Volumes <10K iops during the ",
        dataSource='default',
        targets=target,
        gridPos=GridPos(h=14, w=7, x=17, y=y_pos),
        filterable=True,
        unit="iops",
        displayMode="color-text",
        colorMode="thresholds",
        transformations=transformation,
        timeFrom="2M",
        overrides=json_overrides_table,
        sortBy=table_field_sort,
        )
    )

    pos = pos + 14
    
    return pos, panels_list




########################################################################################################################
#
# FUNCTIONS: Plot a graphic for each metric
#
########################################################################################################################


def gfun_sys_eternus_dx_cpu(system_name, resource_name, metric, y_pos):
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


def gfun_sys_eternus_dx_vol_read(system_name, resource_name, metric, y_pos):
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


def gfun_sys_eternus_dx_vol_write(system_name, resource_name, metric, y_pos):
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


def gfun_sys_eternus_dx_power(system_name, resource_name, metric, y_pos):
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


def gfun_sys_eternus_dx_temp(system_name, resource_name, metric, y_pos):
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


def gfun_sys_eternus_dx_dashboard_vars(system, data):
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


def gfun_sys_eternus_dx_tpp(system_name, resource_name, metric, y_pos):

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

