"""
Serve multiple network transports
+++++++++++++++++++++++++++++++++

Listen and respond to SNMP GET/SET/GETNEXT/GETBULK queries with
the following options:

* SNMPv2c
* with SNMP community "public"
* allow access to SNMPv2-MIB objects (1.3.6.1.2.1)
* over IPv4/UDP, listening at 127.0.0.1:161 and
  over IPv6/UDP, listening at [::1]:161

Either of the following Net-SNMP commands will walk this Agent:

| $ snmpwalk -v2c -c public 127.0.0.1 .1.3.6
| $ snmpwalk -v2c -c public udp6:[::1] .1.3.6

"""  #
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp, udp6

# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Transport setup

# UDP over IPv4 at 127.0.0.1:161
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpTransport().open_server_mode(("127.0.0.1", 161))
)
# UDP over IPv6 at [::1]:161
config.add_transport(
    snmpEngine, udp6.DOMAIN_NAME, udp6.Udp6Transport().open_server_mode(("::1", 161))
)

# SNMPv2c setup

# SecurityName <-> CommunityName mapping.
config.add_v1_system(snmpEngine, "my-area", "public")

# Allow full MIB access for this user / securityModels at VACM
config.add_vacm_user(
    snmpEngine, 2, "my-area", "noAuthNoPriv", (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1)
)

# Get default SNMP context this SNMP engine serves
snmpContext = context.SnmpContext(snmpEngine)

# Register SNMP Applications at the SNMP engine for particular SNMP context
cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

# Register an imaginary never-ending job to keep I/O dispatcher running forever
snmpEngine.transport_dispatcher.job_started(1)

# Run I/O dispatcher which would receive queries and send responses
try:
    snmpEngine.open_dispatcher()
except:
    snmpEngine.close_dispatcher()
    raise
