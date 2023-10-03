

#                       IDENTIFICATION DIVISION



# FJ Data Collector

This is an agentless data collector that populates data in Graphiteapp and since Grafana integrates with Graphite you can draw your graphs in Grafana.

The Collector is a scheduler that collects information based in a YAML file, each schedule runs on it's own thread and it's completly free:
https://github.com/ajcpereira/fj-collector

Regarding the other 2 mention applications be aware of their licenses if you wish to use in your organization.
Our makefile installs both but they are not part of the code of the fj-collector, so you should check your policies or maybe you already have them in your organization so you can use them:

Graphite - https://graphiteapp.org/ - 26/07/2023: (...) Graphite was originally designed and written by Chris Davis at Orbitz in 2006 as side project that ultimately grew to be their foundational monitoring tool. In 2008, Orbitz allowed Graphite to be released under the open source Apache 2.0 license.(...)

Grafana - https://grafana.com/licensing/ - 26/07/2023: (...) On April 20, 2021, Grafana Labs announced that going forward, our core open source projects will be moving from the Apache License v2.0 to AGPLv3.
Users who don’t intend to modify Grafana code can simply use our Enterprise download. This is a free-to-use, proprietary-licensed, compiled binary that matches the features of the AGPL version, and can be upgraded to take advantage of all the commercial features in Grafana Enterprise (Enterprise plugins, advanced security, reporting, support, and more) with the purchase of a license key. (...)

### Requirements

Requires linux

Requires podman

Requires git

Internet access to github.com and docker.io

Will install under folder /opt/fj-collector

Your user must have permissions in /opt and run podman

### Installation Procedure

Get the Makefile and put it in any folder (i.e. /tmp/Makefile)


````
cd /tmp
make install
````

edit /opt/fj-collector/collector/config/collector.yaml

For each IP that you access through ssh you will need the private key and the know_hosts. 
On the previous file (collector.yaml) you can specifie it's location (host_keys entry and known_hosts entry)
Be aware that since the code runs inside a container the collector.yaml uses the path inside of the container, so:
  /collector/fj-collector/config/
  is 
  /opt/fj-collector/collector/config/
 
### collector.yaml
````
solution: 
  platform: 
    - 
      type: CS8000    # Only CS8000 supported atm
      name: MYCS8000
      resources: 
        type: 
          - fs  # fs=filesystem only supported for now
        ip: 
          - 10.0.2.15
        user: report
        proxy: # Leave empty if not using otherwise insert IP/FQDN/HOSTNAME
        poll: 1 # Minute
    - 
      type: CS8000    # Only CS8000 supported
      name: SecondCS8000
      resources: 
        type: 
          - fs # fs=filesystem only supported for now
        ip: 
          - localhost
        user: report
        proxy: # Not supported yet
        poll: 2 # Minutes

parameters:
  repository: graphite
  repository_port: 2003
  repository_protocol: tcp
  host_keys: "/collector/fj-collector/config/id_rsa" # You will have to use a private key - ssh-copy-id username@remote_host, must be done previously
  known_hosts: "/collector/fj-collector/config/known_hosts" # If host is unknown the process will fail
  use_sudo: no
  log: INFO # The log level - DEBUG, INFO, WARNING, ERROR and CRITICAL
````  

### Metrics

Atm we are collecting the iostat for each CS HE filesystem, so you will get filesystem, device multipath and raw device with metrics for:
type: fs
  - svctm
  - %util

### Metrics Retention

You MUST edit the /opt/fj-collector/graphite/data/conf/storage-schemas.conf to change retentions according to your needs:

````
[default_1min_for_1day]
pattern = .*
retentions = 10s:6d,1m:12d,10m:1800d
````

Changing this file will not affect already-created .wsp files. Use whisper-resize.py to change those.

The retentions line is saying that each datapoint represents 10 seconds, and we want to keep enough datapoints so that they add up to 6 hours of data, for 1 minute will keep 6 days and finally for 10 minutes will keep for 1800 days. It will properly downsample metrics (averaging by default) as thresholds for retention are crossed.

More info can be found - https://graphite.readthedocs.io/en/latest/config-carbon.html

### Architecture
![Design](https://github.com/ajcpereira/reporting/raw/main/img/design.png)
