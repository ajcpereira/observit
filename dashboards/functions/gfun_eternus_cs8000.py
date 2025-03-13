
########################################################################################################################
# PROJECT: observIT dashboards container
# DESCRIPTION: eternus_cs8000 graphics creation
# AUTHOR: machadon
# DATE: 2025-03-13
########################################################################################################################

########################################################################################################################
# IMPORTS
########################################################################################################################

from gfun_linux_os import *

########################################################################################################################
#
# CONSTANT DEFINITION
#
########################################################################################################################

GRAPH_ETERNUS_CS8000_FC_DESCRIPTION = (
    "FC Traffic Over Time (Rx/Tx): "
    "This graph displays inbound (Rx) and outbound (Tx) FC traffic across different interfaces, "
    "showing data transfer rates over a given period. "
    "Outbound traffic (Tx) appears above the x-axis, while inbound traffic (Rx) appears below the x-axis. "
    "It helps visualize network activity, track usage patterns, and identify potential anomalies or spikes in traffic."
)


########################################################################################################################
#
# FUNCTIONS: Main Function
#
########################################################################################################################

def gfun_eternus_cs8000_main(system_name, resource_name, data, global_pos):
    panels_list = []
    y_pos = global_pos

    for metric in data:
        match metric['metric']:
            case "fs_io":
                y_pos, panel = gfun_eternus_cs8000_fs_io(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "drives":
                y_pos, panel = gfun_eternus_cs8000_drives(system_name, resource_name, y_pos)
                panels_list = panels_list + panel

            case "medias":
                y_pos, panel = gfun_eternus_cs8000_medias(system_name, resource_name, y_pos)
                panels_list = panels_list + panel

            case "pvgprofile":
                y_pos, panel = gfun_eternus_cs8000_pvgprofile(system_name, resource_name, y_pos)
                panels_list = panels_list + panel

            case "fc":
                y_pos, panel = gfun_eternus_cs8000_fc(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "cpu":
                y_pos, panel = gfun_linux_os_cpu(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "mem":
                y_pos, panel = gfun_linux_os_mem(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "fs":
                y_pos, panel = gfun_linux_os_fs(system_name, resource_name, metric, y_pos)
                #y_pos, panel = graph_eternus_cs8000_fs(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

            case "net":
                y_pos, panel = gfun_linux_os_net(system_name, resource_name, metric, y_pos)
                panels_list = panels_list + panel

    return y_pos, panels_list

def gfun_eternus_cs8000_fs_io(system_name, resource_name, metric, y_pos):
    str_title = "File System IO (" + resource_name + ")"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos)), ]
    pos = y_pos + 1
    panel_width = 5
    panel_height = 14

    for host in metric['hosts']:
        panels_target_list = [InfluxDBTarget(
            query=("SELECT mean(\"svctm\") FROM \"fs_io\" WHERE (\"system\"::tag = '" + system_name +
                   "' AND \"host\"::tag = '" + host +
                   "') AND $timeFilter GROUP BY time($__interval), \"fs\"::tag, \"dm\"::tag, \"rawdev\"::tag fill(null)"),
            alias="$tag_fs $tag_dm $tag_rawdev")]

        panels_list.append(CollectorTimeSeries(
            title=host + " Service Time",
            dataSource='default',
            targets=panels_target_list,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit="ms",
            gridPos=GridPos(h=panel_height, w=panel_width, x=0, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendCalcs=["max", "mean"],
            legendSortBy="Max",
            legendSortDesc=True,
        )
        )

        panels_target_list = [InfluxDBTarget(
            query=("SELECT mean(\"r/s\") FROM \"fs_io\" WHERE (\"system\"::tag = '" + system_name +
                   "' AND \"host\"::tag = '" + host +
                   "') AND $timeFilter GROUP BY time($__interval), \"fs\"::tag, \"dm\"::tag, \"rawdev\"::tag fill(null)"),
            alias="$tag_fs $tag_dm $tag_rawdev")]

        panels_list.append(CollectorTimeSeries(
            title=host + " Reads/s",
            dataSource='default',
            targets=panels_target_list,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit="iops",
            gridPos=GridPos(h=panel_height, w=panel_width, x=1 * panel_width, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendCalcs=["max", "mean"],
            legendSortBy="Max",
            legendSortDesc=True,
        )
        )

        panels_target_list = [InfluxDBTarget(
            query=("SELECT mean(\"r_await\") FROM \"fs_io\" WHERE (\"system\"::tag = '" + system_name +
                   "' AND \"host\"::tag = '" + host +
                   "') AND $timeFilter GROUP BY time($__interval), \"fs\"::tag, \"dm\"::tag, \"rawdev\"::tag fill(null)"),
            alias="$tag_fs $tag_dm $tag_rawdev")]

        panels_list.append(CollectorTimeSeries(
            title=host + " Read Average Wait Time",
            dataSource='default',
            targets=panels_target_list,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit="ms",
            gridPos=GridPos(h=panel_height, w=panel_width, x=2 * panel_width, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendCalcs=["max", "mean"],
            legendSortBy="Max",
            legendSortDesc=True,
        )
        )

        panels_target_list = [InfluxDBTarget(
            query=("SELECT mean(\"w/s\") FROM \"fs_io\" WHERE (\"system\"::tag = '" + system_name +
                   "' AND \"host\"::tag = '" + host +
                   "') AND $timeFilter GROUP BY time($__interval), \"fs\"::tag, \"dm\"::tag, \"rawdev\"::tag fill(null)"),
            alias="$tag_fs $tag_dm $tag_rawdev")]

        panels_list.append(CollectorTimeSeries(
            title=host + " Writes/s",
            dataSource='default',
            targets=panels_target_list,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit="iops",
            gridPos=GridPos(h=panel_height, w=panel_width, x=3 * panel_width, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendCalcs=["max", "mean"],
            legendSortBy="Max",
            legendSortDesc=True,
        )
        )

        panels_target_list = [InfluxDBTarget(
            query=("SELECT mean(\"w_await\") FROM \"fs_io\" WHERE (\"system\"::tag = '" + system_name +
                   "' AND \"host\"::tag = '" + host +
                   "') AND $timeFilter GROUP BY time($__interval), \"fs\"::tag, \"dm\"::tag, \"rawdev\"::tag fill(null)"),
            alias="$tag_fs $tag_dm $tag_rawdev")]

        panels_list.append(CollectorTimeSeries(
            title=host + " Write Average Wait Time",
            dataSource='default',
            targets=panels_target_list,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit="ms",
            gridPos=GridPos(h=panel_height, w=panel_width - 1, x=4 * panel_width, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="bottom",
            legendDisplayMode="table",
            legendCalcs=["max", "mean"],
            legendSortBy="Max",
            legendSortDesc=True,
        )
        )

        pos = pos + 7

    return pos, panels_list


def gfun_eternus_cs8000_drives(system_name, resource_name, y_pos):
    str_title = "Tape Libraries (" + resource_name + ")"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    target_list = [
        InfluxDBTarget(
            query=f"SELECT last(\"total\") as Total FROM \"drives\" "
                  f"WHERE (\"system\"::tag = '{system_name}' AND \"tapename\"::tag =~ /^$tapename$/) AND $timeFilter "
                  f"GROUP BY time($__interval) fill(null)",
            alias=f"Total",
        ),
        InfluxDBTarget(
            query=f"SELECT last(\"used\")+last(\"other\") as Used FROM \"drives\" "
                  f"WHERE (\"system\"::tag = '{system_name}' AND \"tapename\"::tag =~ /^$tapename$/) AND $timeFilter "
                  f"GROUP BY time($__interval) fill(null)",
            alias="Used"
        ),
        InfluxDBTarget(
            query=f"SELECT last(\"other\") as Unavailable FROM \"drives\" "
                  f"WHERE (\"system\"::tag = '{system_name}' AND \"tapename\"::tag =~ /^$tapename$/) AND $timeFilter "
                  f"GROUP BY time($__interval) fill(null)",
            alias="Unavailable"
        ),
    ]

    override_lst = [
        {
            "matcher": {
                "id": "byName",
                "options": "Unavailable"
            },
            "properties": [
                {
                    "id": "custom.fillOpacity",
                    "value": 100
                },
                {
                    "id": "custom.gradientMode",
                    "value": "none"
                },
                {
                    "id": "color",
                    "value": {
                        "fixedColor": "#ff331c",
                        "mode": "fixed"
                    }
                }
            ]
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Total"
            },
            "properties": [
                {
                    "id": "color",
                    "value": {
                        "fixedColor": "blue",
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
                        "fixedColor": "green",
                        "mode": "fixed"
                    }
                }
            ]
        }
    ]

    panels_list.append(CollectorTimeSeries(
        title="Tape Library $tapename",
        repeat=Repeat(direction='h', variable='tapename', maxPerRow=6),
        dataSource='default',
        targets=target_list,
        drawStyle='line',
        lineInterpolation='stepAfter',
        showPoints='auto',
        gradientMode='none',
        fillOpacity=50,
        unit='',
        gridPos=GridPos(h=7, w=12, x=0, y=line),
        spanNulls=COLLECTOR_SPAN_NULLS,
        legendPlacement='right',
        legendDisplayMode='table',
        valueDecimals=0,
        tooltipMode="multi",
        overrides=override_lst,
    )
    )

    line = line + 7

    return line, panels_list


def gfun_eternus_cs8000_medias(system_name, resource_name, y_pos):
    str_title = "Tape Medias (" + resource_name + ")"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    target_list = [InfluxDBTarget(
        query="SELECT  \"Total Cap GiB\" as \"Total Capacity\", \"Total Clean Medias\", \"Total Fault\","
              " \"Total Ina\" as \"Total Inactive\", \"Total Medias\", \"Total Val GiB\" as \"Total Valid\", "
              "\"Val %\" as \"Valid %\"  FROM \"medias\" WHERE $timeFilter AND (\"system\"::tag='" + system_name +
              "') GROUP BY \"host\"::tag, \"tapename\"::tag ORDER BY DESC LIMIT 1",
        format="table")]

    override_lst = [
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
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Total Capacity"
            },
            "properties": [
                {
                    "id": "unit",
                    "value": "decgbytes"
                }
            ]
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Total Valid"
            },
            "properties": [
                {
                    "id": "unit",
                    "value": "decgbytes"
                }
            ]
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Valid %"
            },
            "properties": [
                {
                    "id": "unit",
                    "value": "percent"
                },
                {
                    "id": "thresholds",
                    "value": {
                        "mode": "absolute",
                        "steps": [
                            {
                                "color": "green",
                                "value": None
                            },
                            {
                                "color": "#EAB839",
                                "value": 65
                            },
                            {
                                "color": "red",
                                "value": 75
                            }
                        ]
                    }
                }
            ]
        }
    ]

    thres = [
        {
            "color": "text",
            "value": None
        }
    ]

    panels_list.append(CollectorTable(
        title="Tape Medias",
        dataSource='default',
        targets=target_list,
        gridPos=GridPos(h=7, w=24, x=0, y=line),
        filterable=True,
        displayMode="color-text",
        colorMode="thresholds",
        overrides=override_lst,
        thresholds=thres,
    )
    )

    line = line + 7

    return line, panels_list


def gfun_eternus_cs8000_pvgprofile(system_name, resource_name, y_pos):
    str_title = "Physical Volume Group Profile (" + resource_name + ")"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    line = y_pos + 1

    target_list = [InfluxDBTarget(
        query="SELECT \"Total Medias\", \"Fault\", \"Ina\", \"Scr\", \"-10\", \"-20\", \"-30\", \"-40\", \"-50\", \"-60\", \"-70\", \"-80\", \"-90\", \">90\", \"Total Cap (GiB)\", \"Total Used (GiB)\" from pvgprofile WHERE $timeFilter AND (\"system\"::tag='" + system_name + "') GROUP BY \"pvgname\"::tag, \"host\"::tag ORDER BY DESC LIMIT 1",
        format="table")]

    override_lst = [
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
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Scr"
            },
            "properties": [
                {
                    "id": "thresholds",
                    "value": {
                        "mode": "absolute",
                        "steps": [
                            {
                                "color": "green",
                                "value": None
                            },
                            {
                                "color": "red",
                                "value": 0
                            },
                            {
                                "color": "#EAB839",
                                "value": 10
                            },
                            {
                                "color": "green",
                                "value": 15
                            }
                        ]
                    }
                }
            ]
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Total Cap (GiB)"
            },
            "properties": [
                {
                    "id": "unit",
                    "value": "decgbytes"
                }
            ]
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Total Used (GiB)"
            },
            "properties": [
                {
                    "id": "unit",
                    "value": "decgbytes"
                }
            ]
        }
    ]

    thres = [
        {
            "color": "text",
            "value": None
        }
    ]

    panels_list.append(CollectorTable(
        title="Physical Volume Group",
        dataSource='default',
        targets=target_list,
        gridPos=GridPos(h=7, w=24, x=0, y=line),
        filterable=True,
        displayMode="color-text",
        colorMode="thresholds",
        overrides=override_lst,
        # thresholds=Threshold(line=False,color='text', index=0, value=0.0, op=EVAL_GT),
        thresholds=thres,
        fontSize="85%",
        minWidth=55,
        align="center",
    ))

    line = line + 7

    return line, panels_list


def gfun_eternus_cs8000_fc(system_name, resource_name, metric, y_pos):
    str_title = f"FibreChannel Usage ({resource_name})"
    panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
    pos = y_pos + 1

    for host in metric['hosts']:
        target_net = [
            InfluxDBTarget(
                query=f"SELECT non_negative_derivative(mean(\"tx_bytes\"), 1s)*8 FROM \"fc\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"hba\"::tag fill(null)",
                alias=f"$tag_hba (Tx)"),
            InfluxDBTarget(
                query=f"SELECT non_negative_derivative(mean(\"rx_bytes\"), 1s)*8 FROM \"fc\" "
                      f"WHERE (\"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') AND $timeFilter "
                      f"GROUP BY time($__interval), \"hba\"::tag fill(null)",
                alias=f"$tag_hba (Rx)")
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
            title=host + " FC Traffic",
            dataSource='default',
            targets=target_net,
            drawStyle='line',
            lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
            showPoints=COLLECTOR_SHOW_POINTS,
            gradientMode=COLLECTOR_GRADIENT_MODE,
            fillOpacity=COLLECTOR_FILL_OPACITY,
            unit=COLLECTOR_FC_UNITS,
            gridPos=GridPos(h=7, w=24, x=0, y=pos),
            spanNulls=COLLECTOR_SPAN_NULLS,
            legendPlacement="right",
            legendDisplayMode="table",
            stacking={"mode": "normal", "group": "A"},
            legendSortBy="Name",
            legendCalcs=['mean', 'max'],
            legendSortDesc=False,
            overrides=override_lst,
            description=GRAPH_ETERNUS_CS8000_FC_DESCRIPTION,
        ))

        pos = pos + 7

    return pos, panels_list


