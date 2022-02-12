import os

from dotenv import load_dotenv
import src.api.auth as api_auth
import src.api.host as api_host
import src.api.map as api_map
import src.api.trigger as api_trigger
import src.api.link as api_link
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

def get_router_connections(router_ip: str) -> dict[list, list]:
    load_dotenv()
    snmp_community = os.getenv("SNMP_COMMUNITY")
    connections = []
    remote_hosts_ip = []

    # Get local_hostname
    local_hostname_oid = '1.3.6.1.4.1.9.9.23.1.3.4.0'
    local_hostname_request = snmp_operator.snmp_get(snmp_community, router_ip, local_hostname_oid)
    raw_local_hostname = [str(oid[1]) for oid in local_hostname_request]
    local_hostname = str(raw_local_hostname[0])

    # Get local router mib indexes and remote routers IPs
    raw_local_indexes = snmp_operator.snmp_walk(snmp_community, router_ip, '1.3.6.1.4.1.9.9.23.1.2.1.1.4')
    local_indexes = snmp_utils.extract_indexes_and_ip(raw_local_indexes)
    [connections.append(index) for index in local_indexes]

    # Foreach remotes routers, get the associate info
    for router_info in connections:
        index = router_info['index']
        remote_hostname_oid = '1.3.6.1.4.1.9.9.23.1.2.1.1.6.{}'.format(index)
        local_interface_oid = '1.3.6.1.4.1.9.9.23.1.1.1.1.6.{}'.format(index)
        remote_interface_oid = '1.3.6.1.4.1.9.9.23.1.2.1.1.7.{}'.format(index)
        router_info['local_hostname'] = local_hostname

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

        # Keep track of the remote hosts
        if router_info['remote_ip'] not in remote_hosts_ip:
            remote_hosts_ip.append(router_info['remote_ip'])

        # Remove information not used from now on
        router_info.pop('index')
        router_info.pop('remote_ip')

    return {'routers': connections, 'remote_hosts_ip': remote_hosts_ip}


def build_map(url: str, token: str, zabbix_map: dict, connections: list):
    for connection in connections:
        # Get host's id
        local_host_id = api_host.get_host_id(url, connection["local_hostname"], token)
        remote_host_id = api_host.get_host_id(url, connection["remote_hostname"], token)
        # Get trigger's id
        local_trigger_id = api_trigger.get_id(url, token, local_host_id, connection["local_interface"])
        remote_trigger_id = api_trigger.get_id(url, token, remote_host_id, connection["remote_interface"])

        # Build and add the hosts to the current map if they are not present
        local_host_exist = api_map.host_exist(zabbix_map, local_host_id)
        if local_host_exist == '':
            local_host = api_host.create(connection["local_hostname"], local_host_id)
            zabbix_map['selements'].append(local_host)
        else:
            local_host_id = local_host_exist

        remote_host_exist = api_map.host_exist(zabbix_map, remote_host_id)
        if remote_host_exist == '':
            remote_host = api_host.create(connection["remote_hostname"], remote_host_id)
            zabbix_map['selements'].append(remote_host)
        else:
            remote_host_id = remote_host_exist

        # Build the link
        link_exist = api_map.link_exist(zabbix_map, local_host_id, remote_host_id, local_trigger_id, remote_trigger_id)
        if not link_exist:
            link = api_link.create(local_host_id,
                                   remote_host_id,
                                   connection["local_interface"],
                                   connection["remote_interface"],
                                   local_trigger_id,
                                   remote_trigger_id)

            # Add the link to the current map
            zabbix_map['links'].append(link)

        api_map.update(url, token,  zabbix_map)


def main(url: str, token: str, zabbix_map: dict, routers_ip: list):
    remote_routers_ip = []
    print("remote_routers_ip : {}".format(remote_routers_ip))

    for router_ip in routers_ip:
        routers_info = get_router_connections(router_ip)

        print("------------------------------------------------------------")
        print("-    The following entries will be use to build the map   -")
        print("------------------------------------------------------------")
        [print(x) for x in routers_info['routers']]

        # Populate the zabbix map
        build_map(url, token, zabbix_map, routers_info['routers'])

        # Add remote routers
        for router in routers_info['remote_hosts_ip']:
            if router not in remote_routers_ip:
                remote_routers_ip.append(router)

    print('\nIf you with, the following remote host(s) can be used to continue building the map.')
    print(remote_routers_ip)
    continue_building = input("\nDo you want to continue ? (Yes/No) Default (No) :")

    if continue_building == 'Y' or continue_building == 'Yes':
        print("Map building in progress ...")
        updated_map = api_map.get_by_id(url, token, zabbix_map['sysmapid'])
        main(url, token, updated_map, remote_routers_ip)
    else:
        print("Program ending ...")
        exit()


if __name__ == '__main__':
    load_dotenv()
    # R1 = os.getenv("R1")
    # R2 = os.getenv("R2")
    R3 = os.getenv("R3")

    ZABBIX_URL = os.getenv("ZABBIX_URL")
    MAP_NAME = os.getenv("ZABBIX_MAP_NAME")
    ZABBIX_TOKEN = api_auth.auth(ZABBIX_URL, os.getenv("ZABBIX_USER"), os.getenv("ZABBIX_USER_PASSWORD"))

    # Get the map by name
    current_map = api_map.get_by_name(ZABBIX_URL, ZABBIX_TOKEN, MAP_NAME)

    # Check if the map exist
    if not current_map:
        map_id = api_map.create(ZABBIX_URL, ZABBIX_TOKEN, MAP_NAME)
    else:
        map_id = current_map["sysmapid"]

    # Get back the complete map description
    current_map = api_map.get_by_id(ZABBIX_URL, ZABBIX_TOKEN, map_id)

    # Flush the map from any config
    current_map['selements'].clear()
    current_map['links'].clear()
    api_map.update(ZABBIX_URL, ZABBIX_TOKEN, current_map)

    main(ZABBIX_URL, ZABBIX_TOKEN, current_map, [R3])
