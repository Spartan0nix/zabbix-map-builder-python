import json
import requests
import src.api.auth as api_auth
import src.api.host as api_host
import src.api.map as api_map
import src.api.trigger as api_trigger
import src.api.link as api_link

FIXTURE = {
    "local_hostname": "routeur-1",
    "local_interface": "GigabitEthernet0/1",
    "remote_hostname": "routeur-2",
    "remote_interface": "GigabitEthernet0/2",
}
headers = {'content-type': 'application/json-rpc'}
MAP_NAME = "dev-map-builder"

if __name__ == '__main__':

    # Authentication phase
    with open("env.json") as env_file:
        credentials = json.load(env_file)
        ZABBIX_URL = credentials["url"]
        ZABBIX_TOKEN = api_auth.auth(credentials)

    # Get required information's
    local_host_id = api_host.get_host_id(ZABBIX_URL, FIXTURE["local_hostname"], ZABBIX_TOKEN)
    remote_host_id = api_host.get_host_id(ZABBIX_URL, FIXTURE["remote_hostname"], ZABBIX_TOKEN)
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
    # zabbix_map['selements'] = dict()
    api_map.update(ZABBIX_URL, ZABBIX_TOKEN, zabbix_map)

    # Build the hosts
    local_host = api_host.create(FIXTURE["local_hostname"], local_host_id)
    remote_host = api_host.create(FIXTURE["remote_hostname"], remote_host_id)
    # Get the triggers
    local_trigger_id = api_trigger.get_id(ZABBIX_URL, ZABBIX_TOKEN, local_host_id, FIXTURE["local_interface"])
    remote_trigger_id = api_trigger.get_id(ZABBIX_URL, ZABBIX_TOKEN, remote_host_id, FIXTURE["remote_interface"])
    # Build the link
    link = api_link.create(local_host_id,
                           remote_host_id,
                           FIXTURE["local_interface"],
                           FIXTURE["remote_interface"],
                           local_trigger_id,
                           remote_trigger_id)

    # Add each host to the current map
    zabbix_map['selements'].append(local_host)
    zabbix_map['selements'].append(remote_host)

    # Add the link to the current map
    zabbix_map['links'].append(link)

    api_map.update(ZABBIX_URL, ZABBIX_TOKEN, zabbix_map)

    # TODO Support fixtures multiples (placer la logique de construction dans un foreach)
