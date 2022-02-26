import os
from dotenv import load_dotenv
from src.log.logger import logger
from src.check.api import zabbix_server_reachable
import src.api.auth as api_auth
import src.api.map as api_map
from function import exec_iteration

if __name__ == '__main__':
    load_dotenv()
    ROUTER_IP = os.getenv("ROUTER_IP")
    ZABBIX_URL = os.getenv("ZABBIX_URL")
    MAP_NAME = os.getenv("ZABBIX_MAP_NAME")

    if not zabbix_server_reachable(ZABBIX_URL):
        exit(1)

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
    logger.info("Map was cleared.")

    exec_iteration(ZABBIX_URL, ZABBIX_TOKEN, current_map, [ROUTER_IP])
