import os

from dotenv import load_dotenv
from src.snmp.operator import snmp_get
from src.log.logger import logger


def router_reachable(ip: str) -> bool:
    load_dotenv()
    snmp_community = os.getenv("SNMP_COMMUNITY")
    check_oid = '1.3.6.1.4.1.9.9.23.1.3.4.0'
    try:
        snmp_get(snmp_community, ip, check_oid)
        return True
    except Exception as e:
        logger.warning("Host '{}' is unreachable through SNMP.".format(ip))
        logger.warning('Exception details : {}'.format(e))
        return False
