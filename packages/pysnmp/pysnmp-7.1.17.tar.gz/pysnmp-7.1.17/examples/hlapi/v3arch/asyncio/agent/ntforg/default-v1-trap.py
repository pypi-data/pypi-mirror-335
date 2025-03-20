"""
SNMPv1 TRAP with defaults
+++++++++++++++++++++++++

Send SNMPv1 TRAP through unified SNMPv3 message processing framework
using the following options:

* SNMPv1
* with community name 'public'
* over IPv4/UDP
* send TRAP notification
* with Generic Trap #1 (warmStart) and Specific Trap 0
* with default Uptime
* with default Agent Address
* with Enterprise OID 1.3.6.1.4.1.20408.4.1.1.2
* include managed object information '1.3.6.1.2.1.1.1.0' = 'my system'

Functionally similar to:

| $ snmptrap -v1 -c public demo.pysnmp.com 1.3.6.1.4.1.20408.4.1.1.2 0.0.0.0 1 0 0 1.3.6.1.2.1.1.1.0 s "my system"

"""  #
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


async def run():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
        snmpEngine,
        CommunityData("public", mpModel=0),
        await UdpTransportTarget.create(("demo.pysnmp.com", 162)),
        ContextData(),
        "trap",
        NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2"))
        .load_mibs("SNMPv2-MIB")
        .add_varbinds(
            ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
            ("1.3.6.1.2.1.1.1.0", OctetString("my system")),
        ),
    )

    if errorIndication:
        print(errorIndication)

    snmpEngine.close_dispatcher()


asyncio.run(run())
