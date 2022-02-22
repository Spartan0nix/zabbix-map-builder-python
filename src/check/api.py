import requests
from src.api.utils import headers


def zabbix_server_reachable(zabbix_url: str, ) -> bool:
    print("Checking if the Zabbix Server is reachable. Timeout : 15sec")
    try:
        response = requests.post(zabbix_url, headers=headers, json="", verify=False, timeout=15)
        json_response = response.json()
        if "jsonrpc" and "id" in json_response:
            return True
        return False
    except Exception as e:
        print("!! Zabbix Server unreachable. Reason : {} !!".format(type(e)))
        print("1) Make sure the current network is able to reach the Zabbix Server")
        print("2) check your firewall rules")
        return False
