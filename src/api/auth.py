import requests
from src.api.utils import headers


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
        if "error" in json_response:
            print("Erreur lors de l'authentification au server Zabbix. Raison : {}".format(json_response['error']))
            exit()

        return json_response['result']

    except Exception as e:
        print("Erreur lors de l'authentification au server Zabbix. Raison : {}".format(e))
        exit()
