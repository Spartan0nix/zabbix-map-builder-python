import os

import requests
from dotenv import load_dotenv
import src.api.auth as api_auth
import src.api.host as api_host
import src.api.map as api_map
import src.api.trigger as api_trigger
import src.api.link as api_link

import re
import pysnmp
from pysnmp.hlapi import *
import src.snmp.operator as snmp_operator
import src.snmp.utils as snmp_utils


# FIXTURES = [
#     {
#         "local_hostname": "routeur-1",
#         "local_interface": "GigabitEthernet0/1",
#         "remote_hostname": "routeur-2",
#         "remote_interface": "GigabitEthernet0/1",
#     },
#     {
#         "local_hostname": "routeur-1",
#         "local_interface": "GigabitEthernet0/2",
#         "remote_hostname": "routeur-3",
#         "remote_interface": "GigabitEthernet0/2",
#     },
#     {
#         "local_hostname": "routeur-2",
#         "local_interface": "GigabitEthernet0/3",
#         "remote_hostname": "routeur-3",
#         "remote_interface": "GigabitEthernet0/3",
#     },
#     {
#         "local_hostname": "routeur-4",
#         "local_interface": "GigabitEthernet0/1",
#         "remote_hostname": "routeur-2",
#         "remote_interface": "GigabitEthernet0/1",
#     }
# ]

def build_router_connection(router_ip: str) -> list[dict[str, str, str, str]]:
    routers_info = {'routers': []}

    # Get local_hostname
    local_hostname_oid = '1.3.6.1.4.1.9.9.23.1.3.4.0'
    local_hostname_request = snmp_operator.snmp_get(snmp_community, router_ip, local_hostname_oid)
    local_hostname = [str(oid[1]) for oid in local_hostname_request]
    routers_info['local_hostname'] = str(local_hostname[0])

    # Get local router mib indexes and remote routers IPs
    raw_local_indexes = snmp_operator.snmp_walk(snmp_community, router_ip, '1.3.6.1.4.1.9.9.23.1.2.1.1.4')
    local_indexes = snmp_utils.extract_indexes_and_ip(raw_local_indexes)
    [routers_info['routers'].append(index) for index in local_indexes]

    # Foreach remotes routers, get the associate info
    for router_info in routers_info['routers']:
        index = router_info['index']
        remote_hostname_oid = '1.3.6.1.4.1.9.9.23.1.2.1.1.6.{}'.format(index)
        local_interface_oid = '1.3.6.1.4.1.9.9.23.1.1.1.1.6.{}'.format(index)
        remote_interface_oid = '1.3.6.1.4.1.9.9.23.1.2.1.1.7.{}'.format(index)
        router_info['local_hostname'] = routers_info['local_hostname']

        remote_hostname_request = snmp_operator.snmp_walk(snmp_community, router_ip, remote_hostname_oid)
        for response in remote_hostname_request:
            for oid in response:
                router_info['remote_hostname'] = str(oid[1])

        local_interface_request = snmp_operator.snmp_get(snmp_community, router_ip, local_interface_oid)
        for oid in local_interface_request:
            router_info['local_interface'] = str(oid[1])

        remote_interface_request = snmp_operator.snmp_walk(snmp_community, router_ip, remote_interface_oid)
        for response in remote_interface_request:
            for oid in response:
                router_info['remote_interface'] = str(oid[1])

        router_info.pop('index')
        router_info.pop('remote_ip')

    return routers_info["routers"]


def build_map(connections: list):
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

    for connection in connections:
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


if __name__ == '__main__':
    load_dotenv()

    R1 = os.getenv("R1")
    R2 = os.getenv("R2")
    R3 = os.getenv("R3")
    snmp_community = os.getenv("SNMP_COMMUNITY")

    routers_info = build_router_connection(R3)

    print("------------------------------------------------------------")
    print("-    The following entries will be use to build the map   -")
    print("------------------------------------------------------------")
    [print(x) for x in routers_info]
    # Populate the zabbix map
    build_map(routers_info)
