import requests
from src.api.utils import headers


def get_id(zabbix_url: str, api_token: str, host_id: str, interface: str) -> str:
    data = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "hostids": host_id,
            "filter": {
                "description": {
                    "name": "Interface {} is down".format(interface)
                }
            }
        },
        "auth": api_token,
        "id": 1
    }

    try:
        response = requests.post(zabbix_url, headers=headers, json=data, verify=False)
        json_response = response.json()

        if "error" in json_response:
            print("Erreur lors de la récupération du trigger pour l'hôte : {}. Raison : {}".format(host_id, json_response['error']))
            exit()

        return json_response['result'][0]['triggerid']

    except Exception as e:
        print("Erreur lors de la récupération du trigger pour l'hôte : {}. Raison : {}".format(host_id, e))
        exit()