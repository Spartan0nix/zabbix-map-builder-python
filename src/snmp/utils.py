import re
import pysnmp


def extract_indexes_and_ip(interfaces: list) -> list[dict[str, str]]:
    indexes = []
    for interface in interfaces:
        router_interface = {}
        for oid in interface:
            regex = re.search(
                r"[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]{2}\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.(["
                r"0-9]+)\.[0-9]",
                str(oid[0]))
            index = regex.group(1)

            remote_ip_tuple = oid[1].asNumbers()
            remote_ip = '.'.join(str(x) for x in remote_ip_tuple)

            router_interface['index'] = str(index)
            router_interface['remote_ip'] = str(remote_ip)
            indexes.append(router_interface)

    return indexes


def extract_indexes(oid: str) -> str:
    regex = re.search(r"[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.[0-9]{2}\.[0-9]\.[0-9]\.[0-9]\.[0-9]\.["
                      r"0-9]\.([0-9]+)\.[0-9]", str(oid[0]))
    index = regex.group(1)
    return index
