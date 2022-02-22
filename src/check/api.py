import requests
from src.api.utils import headers
from src.log.logger import logger


def zabbix_server_reachable(zabbix_url: str, ) -> bool:
    try:
        response = requests.post(zabbix_url, headers=headers, json="", verify=False, timeout=15)
        json_response = response.json()
        if 'jsonrpc' and 'id' in json_response:
            return True
        return False
    except Exception as e:
        logger.critical('!! Zabbix Server unreachable. Reason : {} !!'.format(e))
        logger.critical('1) Make sure the current network is able to reach the Zabbix Server')
        logger.critical('2) check your firewall rules')
        return False
