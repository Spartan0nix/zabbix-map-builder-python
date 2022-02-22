import requests
from src.api.utils import headers
from src.log.logger import logger


def get_host_id(zabbix_url: str, hostname: str, api_token: str) -> str:
    data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "filter": {
                "host": [
                    hostname
                ]
            }
        },
        "auth": api_token,
        "id": 1
    }

    try:
        response = requests.post(zabbix_url, headers=headers, json=data, verify=False)
        json_response = response.json()
        if 'error' in json_response:
            logger.error("Error while retrieving host_id for host '{}'. Reason : {}".format(hostname, json_response['error']))
            exit(1)
        return json_response['result'][0]['hostid']
    except Exception as e:
        logger.error("Error while retrieving host_id for host '{}'.Reason : {}".format(hostname, e))
        exit(1)


def create(name: str, host_id: str) -> dict:
    return {
        "selementid": host_id,
        "elementtype": 0,
        "elements": [{
            "hostid": host_id
        }],
        "iconid_off": "156",
        "label": name,
        "label_location": "-1",
        "inherited_label": name,
        "label_type": "2",
        "elementName": name
    }
