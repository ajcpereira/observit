#!/bin/bash

# Function to update the OS
update_os() {
    sudo apt-get update 
    echo "Press any key to upgrade now"
    read
    sudo apt-get upgrade -y 
    echo "Press any key to upgrade release if new is available"
    read
    sudo /usr/bin/do-release-upgrade
    echo "Press any to return to setup"
    read
}

# Function for containers house keeping
house_keeping() {
    MYOUTPUT=`docker system prune -a -f; docker volume prune -a -f; docker image prune -a -f`
    # Display summary of network settings
    dialog --title "Result" --msgbox \
        "$MYOUTPUT" 10 50
}


# Function to change network settings
function change_network {
    # Create a temporary file to store the input data
    TEMP_FILE=$(mktemp)

    # Display the menu with all fields in one form
    dialog --backtitle "Network Configuration" --title "Network Input" \
        --form "\nDialog Sample Label and Values" 25 60 16 \
        "IP Address (CIDR):" 1 1 "10.1.1.1/24" 1 25 25 30 \
        "Gateway:" 2 1 "" 2 25 25 30 \
        "DNS (Comma separated):" 3 1 "" 3 25 25 30 \
        2>$TEMP_FILE
    
    interface=`ip -o link show | grep -v lo | awk '{print $2}' | sed 's/://g' | head -1`

    # Check if ESC was pressed (exit status 1 means ESC or Cancel was pressed)
    if [[ $? -ne 0 ]]; then
        return 1  # Return to the previous menu
    else
        # Read the values from the temporary file
        readarray -t values < $TEMP_FILE
        IP_CIDR="${values[0]}"
        GATEWAY="${values[1]}"
        DNS="${values[2]}"

        # Remove the temporary file
        rm -f $TEMP_FILE

        # Clean up IP_CIDR to remove any trailing slashes
        echo $IP_CIDR > /tmp/pre
        IP_CIDR=$(echo $IP_CIDR | sed 's/\/$//')
        echo $IP_CIDR > /tmp/pos

        # Display summary of network settings
        dialog --title "Network Settings Summary" --msgbox \
            "IP Address: $IP_CIDR\nGateway: $GATEWAY\nDNS: $DNS" 10 50

        # Validate the IP address format
        if [[ $IP_CIDR =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+$ ]]; then
            # Validate the gateway format
            if [[ $GATEWAY =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                echo $IP_CIDR >> /tmp/pos
                # Update the network configuration file
                if [ -f /tmp/network_file.tmp ]; then
                   rm -f /tmp/network_file.tmp
                fi
                bash -c "cat > /tmp/network_file.tmp <<EOF
network:
  version: 2
  ethernets:
    $interface:
      addresses: [$IP_CIDR]
      routes:
       - to: default
         via: $GATEWAY
      nameservers:
        addresses: [$DNS]
EOF"
                chmod 400 /tmp/network_file.tmp
                sudo cp -p /tmp/network_file.tmp /etc/netplan/01-netcfg.yaml
                sudo netplan apply
            else
                dialog --title "Network Settings Summary" --msgbox \
                    "Invalid Gateway format. Please enter a valid IP address." 10 50
            fi
        else
            dialog --title "Network Settings Summary" --msgbox \
                "Invalid IP address format. Please enter a valid IP address in CIDR notation." 10 50
        fi
    fi

    return 0  # Return success
}

# Function to change keyboard layout
change_keyboard() {
    KEYBOARD=$(dialog --menu "Choose a keyboard layout:" 15 50 10 $(localectl list-x11-keymap-layouts | awk '{print NR, $1}') 3>&1 1>&2 2>&3 3>&-)
    sudo loadkeys $KEYBOARD
}

# Function to change timezone
change_timezone() {
    TIMEZONE=$(dialog --menu "Choose a timezone:" 15 50 10 $(timedatectl list-timezones | awk '{print NR, $1}') 3>&1 1>&2 2>&3 3>&-)
    sudo timedatectl set-timezone $TIMEZONE
}

make_dhcp() {
    sudo rm /etc/netplan/01-netcfg.yaml
    sudo netplan apply
}

genkey(){
    DEVICE=$(ip -o link show | grep -v lo | awk '{ print $2 }' | sed 's/://g' | head -1)
    IP=$(ip -4 addr show $DEVICE | grep inet | awk '{ print $2 }'| cut -d'/' -f1 | sed 's/\.//g')
    MAC=$(ip link show $DEVICE | awk '/ether/ {print $2}'| sed 's/://g')

    # Display summary of the key
    dialog --title "Key to generate License" --msgbox \
            "KEY: $MAC$IP \n\nIt will also be available in /tmp/req_licensekey.obs" 10 50

    echo "$MAC$IP" > /tmp/req_licensekey.obs
}

build_collector() {
    cd /home/observit/observit

    DEVICE=$(ip -o link show | grep -v lo | awk '{ print $2 }' | sed 's/://g' | head -1)
    IP=$(ip -4 addr show $DEVICE | grep inet | awk '{ print $2 }'| cut -d'/' -f1 | sed 's/\.//g')
    MAC=$(ip link show $DEVICE | awk '/ether/ {print $2}'| sed 's/://g')
    INTERFACE=$MAC$IP
    export INTERFACE

	docker compose stop observit
    docker compose stop dashboards
    

	docker compose images rm observit-observit-1
    docker compose images rm observit-dashboards-1


	cp ./install/Dockerfile .
    if [ ! -d /opt/observit/telegraf/config ]; then
       mkdir -p /opt/observit/telegraf/config
       cp ./config/telegraf.conf /opt/observit/telegraf/config
    elif [ ! -f /opt/observit/telegraf/config/telegraf.config ];then
       cp ./config/telegraf.conf /opt/observit/telegraf/config
    fi

	docker build . -t observit:latest
	docker compose create observit

	docker compose start observit
    docker compose up -d

	rm Dockerfile

    docker system prune -a -f; docker volume prune -a -f; docker image prune -a -f
}

# Function to manage containers
manage_containers() {

    CONTAINERS=$(docker ps -a --format "{{.Names}} - {{.Status}}" | awk '{print NR, $0}')
    if [ -z "$CONTAINERS" ]; then
        dialog --title "Containers Summary" --msgbox \
        "There are no containers running. Some manual intervention was made, please contact support." 10 50
    else
        # Replace spaces with underscores in status part only
        MENU_OPTIONS=$(echo "$CONTAINERS" | awk '{status=$2; for(i=3; i<=NF; i++) status=status" "$i; gsub(/ /,"_",status); print $1, status}')

        # Pass the modified container list to dialog
        CONTAINER=$(dialog --menu "Select a container to manage:" 15 50 10 $MENU_OPTIONS 3>&1 1>&2 2>&3 3>&-)

        # Replace underscores back to spaces after the selection
        CONTAINER=$(echo "$CONTAINER" | sed 's/_/ /g')

        # Output the selected container for debugging purposes
        echo "You selected: $CONTAINER"
    fi


    
    
    if [ -n "$CONTAINER" ]; then
        ACTION=$(dialog --menu "Choose an action for $CONTAINER:" 15 50 5 \
        1 "Start" \
        2 "Stop" \
        3 "Restart" 3>&1 1>&2 2>&3 3>&-)

        case $ACTION in
            1)
                docker start $(echo $CONTAINERS | tr ' ' '\n' | awk -v action="$CONTAINER" 'NR % 2 == 1 && $1 == action {getline; print $0}')
                ;;
            2)
                docker stop $(echo $CONTAINERS | tr ' ' '\n' | awk -v action="$CONTAINER" 'NR % 2 == 1 && $1 == action {getline; print $0}')
                ;;
            3)
                docker restart $(echo $CONTAINERS | tr ' ' '\n' | awk -v action="$CONTAINER" 'NR % 2 == 1 && $1 == action {getline; print $0}')
                ;;
        esac
    fi
}

# Main menu
while true; do
    CHOICE=$(dialog --menu "System Configuration Menu" 15 50 6 \
    1 "Update OS" \
    2 "Change Network Settings" \
    3 "Manage Containers" \
    4 "House Keeping for containers" \
    5 "Enable DHCP" \
    6 "Change timezone" \
    7 "Build Container" \
    8 "GenKey" \
    9 "Exit" 3>&1 1>&2 2>&3 3>&-)
    
    case $CHOICE in
        1)
            update_os
            ;;
        2)
            change_network
            ;;
        3)
            manage_containers
            ;;
        4)
            house_keeping
            ;;
        5)
            make_dhcp
            ;;
        6)
            change_timezone
            ;;
        7)
            build_collector
            ;;
        8)
            genkey
            ;;
        9)
            clear
            break
            ;;
        *)
            clear
            break
            ;;
    esac
done
