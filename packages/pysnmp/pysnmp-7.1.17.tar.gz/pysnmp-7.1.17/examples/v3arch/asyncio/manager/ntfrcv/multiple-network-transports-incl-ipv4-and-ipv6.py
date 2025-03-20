"""
Using multiple network transports
+++++++++++++++++++++++++++++++++

Receive SNMP TRAP/INFORM messages with the following options:

* SNMPv1/SNMPv2c
* with SNMP community "public"
* over IPv4/UDP, listening at 127.0.0.1:162
  over IPv6/UDP, listening at [::1]:162
* print received data on stdout

Either of the following Net-SNMP commands will send notifications to this
receiver:

| $ snmptrap -v1 -c public 127.0.0.1 1.3.6.1.4.1.20408.4.1.1.2 127.0.0.1 1 1 123 1.3.6.1.2.1.1.1.0 s test
| $ snmptrap -v2c -c public udp6:[::1]:162 123 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.5.0 s test
| $ snmpinform -v2c -c public 127.0.0.1 123 1.3.6.1.6.3.1.1.5.1

"""  #
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pysnmp.entity.rfc3413 import ntfrcv

# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Transport setup

# UDP over IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpTransport().open_server_mode(("127.0.0.1", 162))
)

# UDP over IPv6
config.add_transport(
    snmpEngine, udp6.DOMAIN_NAME, udp6.Udp6Transport().open_server_mode(("::1", 162))
)

# SNMPv1/2c setup

# SecurityName <-> CommunityName mapping
config.add_v1_system(snmpEngine, "my-area", "public")


# Callback function for receiving notifications
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    print(
        'Notification from ContextEngineId "{}", ContextName "{}"'.format(
            contextEngineId.prettyPrint(), contextName.prettyPrint()
        )
    )
    for name, val in varBinds:
        print(f"{name.prettyPrint()} = {val.prettyPrint()}")


# Register SNMP Application at the SNMP engine
ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transport_dispatcher.job_started(1)  # this job would never finish

# Run I/O dispatcher which would receive queries and send confirmations
try:
    snmpEngine.open_dispatcher()
except:
    snmpEngine.close_dispatcher()
    raise
