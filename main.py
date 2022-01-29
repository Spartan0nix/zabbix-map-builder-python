import os
import requests
from dotenv import load_dotenv
import src.api.auth as api_auth
import src.api.host as api_host
import src.api.map as api_map
import src.api.trigger as api_trigger
import src.api.link as api_link

FIXTURES = [
    {
        "local_hostname": "routeur-1",
        "local_interface": "GigabitEthernet0/1",
        "remote_hostname": "routeur-2",
        "remote_interface": "GigabitEthernet0/1",
    },
    {
        "local_hostname": "routeur-1",
        "local_interface": "GigabitEthernet0/2",
        "remote_hostname": "routeur-3",
        "remote_interface": "GigabitEthernet0/2",
    },
    {
        "local_hostname": "routeur-2",
        "local_interface": "GigabitEthernet0/3",
        "remote_hostname": "routeur-3",
        "remote_interface": "GigabitEthernet0/3",
    },
    {
        "local_hostname": "routeur-4",
        "local_interface": "GigabitEthernet0/1",
        "remote_hostname": "routeur-2",
        "remote_interface": "GigabitEthernet0/1",
    }
]

if __name__ == '__main__':

    load_dotenv()

    ZABBIX_URL = os.getenv("ZABBIX_URL")
    MAP_NAME = os.getenv("ZABBIX_MAP_NAME")
    ZABBIX_TOKEN = api_auth.auth(ZABBIX_URL, os.getenv("ZABBIX_USER"), os.getenv("ZABBIX_USER_PASSWORD"))
    map_hosts = []

    # Get the map by name
    zabbix_map = api_map.get_by_name(ZABBIX_URL, ZABBIX_TOKEN, MAP_NAME)

    # Check if the map exist
    if not zabbix_map:
        map_id = api_map.create(ZABBIX_URL, ZABBIX_TOKEN, MAP_NAME)
    else:
        map_id = zabbix_map["sysmapid"]

    # Retrieve the map
    zabbix_map = api_map.get_by_id(ZABBIX_URL, ZABBIX_TOKEN, map_id)

    # Flush the map from any host
    zabbix_map['selements'].clear()
    zabbix_map['links'].clear()
    api_map.update(ZABBIX_URL, ZABBIX_TOKEN, zabbix_map)

    for connection in FIXTURES:
        # Get host's id
        local_host_id = api_host.get_host_id(ZABBIX_URL, connection["local_hostname"], ZABBIX_TOKEN)
        remote_host_id = api_host.get_host_id(ZABBIX_URL, connection["remote_hostname"], ZABBIX_TOKEN)
        # Get trigger's id
        local_trigger_id = api_trigger.get_id(ZABBIX_URL, ZABBIX_TOKEN, local_host_id, connection["local_interface"])
        remote_trigger_id = api_trigger.get_id(ZABBIX_URL, ZABBIX_TOKEN, remote_host_id, connection["remote_interface"])

        # Build and add the hosts to the current map if they are not present
        if local_host_id not in map_hosts:
            local_host = api_host.create(connection["local_hostname"], local_host_id)
            zabbix_map['selements'].append(local_host)

            # Update the tracking hosts list
            map_hosts.append(local_host_id)

        if remote_host_id not in map_hosts:
            remote_host = api_host.create(connection["remote_hostname"], remote_host_id)
            zabbix_map['selements'].append(remote_host)

            # Update the tracking hosts list
            map_hosts.append(remote_host_id)

        # Build the link
        link = api_link.create(local_host_id,
                               remote_host_id,
                               connection["local_interface"],
                               connection["remote_interface"],
                               local_trigger_id,
                               remote_trigger_id)

        # Add the link to the current map
        zabbix_map['links'].append(link)

        api_map.update(ZABBIX_URL, ZABBIX_TOKEN, zabbix_map)
