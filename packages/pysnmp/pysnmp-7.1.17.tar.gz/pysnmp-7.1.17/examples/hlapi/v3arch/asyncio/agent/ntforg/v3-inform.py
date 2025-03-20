"""
INFORM, auth: MD5 privacy: DES
++++++++++++++++++++++++++++++
Send SNMP INFORM notification using the following options:
* SNMPv3
* with user 'usr-md5-des', auth: MD5, priv DES
* over IPv4/UDP
* send INFORM notification
* with TRAP ID 'warmStart' specified as a string OID
* include managed object information 1.3.6.1.2.1.1.5.0 = 'system name'
Functionally similar to:
| $ snmpinform -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 demo.pysnmp.com 12345 1.3.6.1.4.1.20408.4.1.1.2 1.3.6.1.2.1.1.1.0 s "my system"
"""  #

import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


async def run():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
        snmpEngine,
        UsmUserData("usr-md5-des", "authkey1", "privkey1"),
        await UdpTransportTarget.create(("demo.pysnmp.com", 162)),
        ContextData(),
        "inform",
        NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2"))
        .add_varbinds(ObjectType(ObjectIdentity("1.3.6.1.2.1.1.5.0"), "system name"))
        .load_mibs("SNMPv2-MIB"),
    )

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print(
            "{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )

    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))

    snmpEngine.close_dispatcher()


asyncio.run(run())
