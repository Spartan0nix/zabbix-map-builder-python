from pysnmp.hlapi import *


def snmp_walk(community: str, ip: str, oid: str) -> list:
    result = []
    operation = nextCmd(SnmpEngine(),
                        CommunityData(community, mpModel=1),
                        UdpTransportTarget((ip, 161)),
                        ContextData(),
                        ObjectType(ObjectIdentity(oid)),
                        lexicographicMode=False)

    for (errorIndication, errorStatus, errorIndex, varBinds) in operation:
        if errorIndication:
            raise Exception(errorIndication)
        if errorStatus:
            raise Exception(errorStatus)
        if errorIndication:
            raise Exception(errorIndication)
        if not errorIndication and not errorStatus:
            result.append(varBinds)
    return result


def snmp_get(community: str, ip: str, oid: str) -> list:
    result = []
    operation = getCmd(SnmpEngine(),
                       CommunityData(community, mpModel=1),
                       UdpTransportTarget((ip, 161)),
                       ContextData(),
                       ObjectType(ObjectIdentity(oid)))

    for (errorIndication, errorStatus, errorIndex, varBinds) in operation:
        if errorIndication:
            raise Exception(errorIndication)
        if errorStatus:
            raise Exception(errorStatus)
        if errorIndication:
            raise Exception(errorIndication)
        if not errorIndication and not errorStatus:
            result.append(varBinds[0])
    return result
