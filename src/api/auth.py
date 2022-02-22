import requests
from src.api.utils import headers
from src.log.logger import logger


def auth(url: str, user: str, password: str) -> str:
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": user,
            "password": password
        },
        "id": 1
    }

    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        json_response = response.json()
        if 'error' in json_response:
            logger.error(logger.ERROR, 'Error while retrieving the Zabbix API Token. Reason : {}'.format(
                json_response['error']))
            exit(1)
        return json_response['result']
    except Exception as e:
        logger.error('Error while retrieving the Zabbix API Token. Reason : {}'.format(e))
        exit(1)

