import requests
from src.api.utils import headers
from src.log.logger import logger


def get_by_id(zabbix_url: str, api_token: str, map_id: str) -> dict:
    data = {
        "jsonrpc": "2.0",
        "method": "map.get",
        "params": {
            "output": "extend",
            "selectSelements": "extend",
            "selectLinks": "extend",
            "selectUsers": "extend",
            "selectUserGroups": "extend",
            "selectShapes": "extend",
            "selectLines": "extend",
            "sysmapids": map_id
        },
        "auth": api_token,
        "id": 1
    }

    try:
        response = requests.post(zabbix_url, headers=headers, json=data, verify=False)
        json_response = response.json()
        if 'error' in json_response:
            logger.error(
                "Error while retrieving map with id '{}' found. Reason : {}.".format(map_id, json_response['error']))
            exit(1)
        return json_response['result'][0]
    except Exception as e:
        logger.error("No map with id '{}' found. Reason : {}.".format(map_id, e))
        exit(1)


def get_by_name(zabbix_url: str, api_token: str, name: str) -> dict:
    data = {
        "jsonrpc": "2.0",
        "method": "map.get",
        "params": {
            "search": {
                "name": name
            }
        },
        "auth": api_token,
        "id": 1
    }

    try:
        response = requests.post(zabbix_url, headers=headers, json=data, verify=False)
        json_response = response.json()

        if 'error' in json_response['result']:
            logger.error(
                "Error while retrieving map with name '{}' found. Reason : {}.".format(name, json_response['error']))
            exit(1)
        if json_response['result']:
            return json_response['result'][0]
        else:
            return []
    except Exception as e:
        logger.error("Error while retrieving map with name '{}' found. Reason : {}.".format(name, e))
        exit(1)


def create(zabbix_url: str, api_token: str, name: str) -> str:
    data = {
        "jsonrpc": "2.0",
        "method": "map.create",
        "params": {
            "name": name,
            "width": 600,
            "height": 600
        },
        "auth": api_token,
        "id": 1
    }

    try:
        response = requests.post(zabbix_url, headers=headers, json=data, verify=False)
        json_response = response.json()

        if 'error' in json_response:
            logger.error(
                "Error while creating map with name '{}' found. Reason : {}.".format(name, json_response['error']))
            exit(1)
        return json_response['result']['sysmapids'][0]
    except Exception as e:
        logger.error("Error while creating map with name '{}' found. Reason : {}.".format(name, e))
        exit(1)


def update(zabbix_url: str, api_token: str, zabbix_map: dict) -> str:
    data = {
        "jsonrpc": "2.0",
        "method": "map.update",
        "params": zabbix_map,
        "auth": api_token,
        "id": 1
    }

    try:
        response = requests.post(zabbix_url, headers=headers, json=data, verify=False)
        json_response = response.json()

        if 'error' in json_response:
            logger.error("Error while updating map with id '{}' found. Reason : {}.".format(zabbix_map["sysmapid"],
                                                                                            json_response["error"]))
            exit(1)
        map_id = json_response['result']['sysmapids'][0]
        logger.info("Map with id '{}' updated.".format(map_id))
        return map_id
    except Exception as e:
        logger.error("Error while updating map with id '{}' found. Reason : {}.".format(zabbix_map['sysmapid'], e))
        exit(1)


def host_exist(zabbix_map: dict, host_id: str) -> str:
    for host in zabbix_map['selements']:
        if host['elements'][0]['hostid'] == host_id:
            return host['selementid']
    return ''


def link_exist(zabbix_map: dict,
               local_host_id: str,
               remote_host_id: str,
               local_trigger_id: str,
               remote_trigger_id: str
               ) -> bool:
    for link in zabbix_map['links']:
        if link['selementid1'] == local_host_id and link['selementid2'] == remote_host_id:
            if link['linktriggers'][0]['triggerid'] == local_trigger_id \
                    and link['linktriggers'][1]['triggerid'] == remote_trigger_id:
                return True
        if link['selementid1'] == remote_host_id and link['selementid2'] == local_host_id:
            if link['linktriggers'][0]['triggerid'] == remote_trigger_id \
                    and link['linktriggers'][1]['triggerid'] == local_trigger_id:
                return True
    return False
