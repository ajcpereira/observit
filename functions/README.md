# Available Functions

Here you will find the information for each resource type and respective metrics

## resources_types: eternus_cs8000

Protocol: ssh<br>
Security: The user must be created previously and the public key must exist in the destination system. The process is documented in the main README.md<br>
### Metrics:<br>
  #### fs_io<br>

    Reports the "svctm", "r_await", "w_await", "r/s" and "w/s" for each filesystem/dm/rawdevice
    sudo is required: In /etc/sudoers you must have "observit CSTOR = NOPASSWD: /opt/fsc/CentricStor/bin/rdNsdInfos -a"
    If file cafs_iostat exists under the dir tests it will be used instead of real data.
  
  #### drives<br>

    Reports the drive occupation for each physical library
    sudo is required: In /etc/sudoers you must have "observit CSTOR = NOPASSWD: /opt/fsc/bin/plmcmd query *"
  
  #### pvgprofile<br>
    Reports for each PVG the following "Total Medias" "Fault Medias" "Inacessible Medias" "Scratch Medias" "Medias with -10%, -20%, -30%, -40%, -50%, -60%, -70%, -80%, -90% and >90% valid LV's" "Total Cap (GiB)" "Total Used (GiB)"
    sudo is required: In /etc/sudoers you must have "observit CSTOR = NOPASSWD: /opt/fsc/bin/plmcmd query *"
  
  #### medias<br>
    Reports all medias: "Total Medias" "Total Cap GiB" "Total Val GiB" "Val %" "Total Clean Medias" "Total Ina" "Total Fault"
    sudo is required: In /etc/sudoers you must have "observit CSTOR = NOPASSWD: /opt/fsc/bin/plmcmd query *"
  
  #### fs<br>
  
    Reports, for each mount point, the "available", "used", "total" filesystem usage in KB for each system
  
  #### cpu<br>
  
    Reports the cpu  "use", "iowait", "load1m", "load5m", "load15m" usage in each system.
  
  #### mem<br>
  
    Reports the memory "total", "used", "free", "shared", "buff", "avail" usage in MB for each system
  
  #### fc<br>
  
    Reports the fc throughput in each HBA, including the targets that are virtual drives
  
  #### net<br>
  
    Reports the acumulated "rx_bytes", "tx_bytes" for each NIC.

  #### vtldirtycache<br>

    Reports the dirty cache for the VTL system
      
## resources_types: linux_os

Protocol: ssh<br>
Security: The user must be created previously and the public key must exist in the destination system. The process is documented in the main README.md<br>
### Metrics:<br>

  #### cpu<br>

    Reports the cpu  "use", "iowait", "load1m", "load5m", "load15m" usage in each system.

  #### mem<br>

    Reports the memory "total", "used", "free", "shared", "buff", "avail" usage in MB for each system

  #### fs<br>

    Reports, for each mount point, the "available", "used", "total" filesystem usage in KB for each system

  #### net<br>

     Reports the acumulated "rx_bytes", "tx_bytes" for each NIC.

### Config File example<br>

````
systems:
  - name: LAB
    resources_types: linux_os
    config:
      parameters:
          user: observit
          host_keys: keys/id_rsa
          poll: 1
          use_sudo: no
          bastion: 127.0.0.1
      metrics:
          - name: cpu
          - name: mem
          - name: fs
          - name: net
      ips:
          - ip: 127.0.0.1
            alias: linux01
            ip_use_sudo: yes
            ip_host_keys: keys/127.0.0.1_rsa
            ip_bastion: 127.0.0.1
          - ip: 127.0.0.1
            alias: linux02
            ip_use_sudo: yes
            ip_host_keys: keys/127.0.0.1_rsa
            ip_bastion: 127.0.0.1
  - name: LAB
    resources_types: eternus_cs8000
    config:
      parameters:
          user: observit
          host_keys: keys/id_rsa
          poll: 1
          use_sudo: no
          bastion: 127.0.0.1
      metrics:
          - name: drives
          - name: fs_io
          - name: medias
          - name: pvgprofile
      ips:
          - ip: 127.0.0.1
            alias: linux01
            ip_use_sudo: yes
            ip_host_keys: keys/127.0.0.1_rsa
            ip_bastion: 127.0.0.1
          - ip: 127.0.0.1
            alias: linux02
            ip_use_sudo: yes
            ip_host_keys: keys/127.0.0.1_rsa
            ip_bastion: 127.0.0.1
global_parameters:
    repository: influxdb
    repository_port: 8086
    repository_protocol: tcp
    repository_api_key: TOBEDEFINEDINSETUP
    loglevel: WARNING
    logfile: logs/observit.log
    auto_fungraph: yes
    grafana_api_key: TOBEDEFINEDINSETUP
    grafana_server: grafana
````
