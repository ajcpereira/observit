# ObservIT
![Logo](https://github.com/ajcpereira/observIT/blob/main/img/ObservIT.jpg)

This is an aggregator for data collection that populates data in InfluxDB and uses Grafana which integrates natively with Infludb where you can draw your graphs, we also may use Telegraf to speed some integrations since InfluxData are the builders of Influxdb and Telegraf. 
<BR>We draw our standard graphs for each of the metrics we support but please feel free to personalize your own graphics.

<BR>Please Consult our wiki if you wish to contribute with new metrics [https://github.com/ajcpereira/observIT.wiki.git](https://github.com/ajcpereira/observIT/wiki/Development-Rules-%E2%80%90-New-Function-using-ssh)

## How it Works

The aggregator is a scheduler that collects information based in a YAML file (/opt/observit/collector/conf/config.yaml), each schedule runs on it's own thread and it uses python, all the supported metrics may be found here:
<BR>https://github.com/ajcpereira/observit/blob/main/functions/README.md

This is built on a virtual appliance which can be found here: 
<BR>https://drive.proton.me/urls/6WE4036KX8#dHQ35JnT8Obz

<BR>If you are running in Hyper-V please make sure that "Enable Secure Boot" is enabled with "Microsoft UEFI Certificate Authority" 
<BR>Once you enter in the system just run "setup" and you may change the ip. The only user available to you will be observit and by default user and password are equal, please change this password as soon as you login.

<BR>You can make OS updates for security reasons also the "setup" command.

## Licensing
Regarding the 3 mention applications be aware of their licenses if you wish to use in your organization.
We install both but they are not part of the code of the ObservIT, so you should check your policies or maybe you already have them in your organization and you just need to change the configfile to use your own:

|Components		|Licensing                                                  |
|---------------|:---------------------------------------------------------:|
|Ubuntu			|https://ubuntu.com/legal/intellectual-property-policy      |
|git			|https://git-scm.com/about/free-and-open-source             |
|docker engine	|https://github.com/moby/moby/blob/master/LICENSE     |
|Python			|https://opensource.org/license/python-2-0                  |
|Grafana		|https://grafana.com/licensing/                             |
|Influxdb		|https://github.com/influxdata/influxdb/blob/master/LICENSE |
|Telegraf   |https://github.com/influxdata/telegraf/blob/master/LICENSE |

## Technical Section
### Requirements

You need a virtualization environment, our virtual appliance, for a basic configuation up to 80 metrics needs the following requirements:

| vCPU          | Mem           | Disk      |
| ------------- |:-------------:| ---------:|
| 4             | 8GB           | 30GB+15GB |

*The 15GB disk can grow to accomodate your retention period, you will need the root access at this moment until we give you a script to do so with observit user.


### Pre-Setup

Every metric that needs to make ssh, make sure you generate a private key and in the destination you use the public key in the authorized keys, then keep the private keys under:
<BR>/opt/observit/collector/keys
If different keys are used they may be specified in the config.yaml

Under the user observit, pls do:

````
ssh-keygen -t rsa -b 2048
````

you can accept defaults with no passphrase. The files will be created under observit/.ssh/id_rsa for the private key and observit/.ssh/id_rsa.pub for the public key.

The private key should be specified in the config.yaml file, because it's running under a container, we recommend to put under /opt/observit/collector/keys.

The public key must be added to the user used for the login (we assume observit) so, /home/observit/.ssh/authorized_keys owned by observit and with 600 permissions, and the .ssh directory should be 700 with owner observit.

If you are using a CS8000 the user must be created using:
````
ecs-add-user --user=observit --role=csobserve
````
Keep in mind that some metrics require sudo permissions, set them accordingly

We recommend to you have a look in the functions Readme:
<BR>https://github.com/ajcpereira/observit/blob/main/functions/README.md

We recommend you use relative paths:
    <BR>host_keys: keys/id_rsa
    <BR>logfile: logs/observit.log

edit /opt/observit/collector/config/config.yaml

### config.yaml
Configuration manual can be found in https://github.com/ajcpereira/observit/blob/main/config/README.md

````
systems:
  - name: MYCS0100
    resources_types: eternus_cs8000
    config:
      parameters:
        user: observit
        host_keys: keys/id_rsa
        poll: 1
      metrics:
        - name: fs_io
        - name: fs
        - name: cpu
        - name: mem
        - name: drives
      ips:
        - ip:  192.168.18.46
          alias: linux14
        - ip:  192.168.18.46
          alias: linux02
global_parameters:
  repository: influxdb
  repository_port: 8086
  repository_protocol: tcp
  repository_api_key: AUTOGENERATED_DURING_SETUP
  loglevel: DEBUG
  logfile: logs/observit.log
  auto_fungraph: yes
  grafana_api_key: AUTOGENERATED_DURING_SETUP
  grafana_server: grafana
````  

### Metrics

Consult the README inside the folder functions:
<BR>https://github.com/ajcpereira/observit/blob/main/functions/README.md

### Metrics Retention

By default the bucket that will retain the information in Influxdb is of **2 years**, manual change must be done if you wish to have a different retention.
At the moment this must be done with user admin in the future we expect to give this through scripting or other way.


### Architecture
![Design](https://github.com/ajcpereira/reporting/raw/main/img/design.png)
