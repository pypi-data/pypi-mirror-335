"""
Notification over multiple network protocols
++++++++++++++++++++++++++++++++++++++++++++

Send SNMP INFORM notifications to multiple Managers over different
network protocols:

* SNMPv2c
* with community name 'public'
* over IPv4/UDP and UDP/IPv6
* send TRAP notification
* to two Managers through different network transports
* with TRAP ID 'coldStart' specified as an OID
* include managed objects information:
  1.3.6.1.2.1.1.1.0 = 'Example Notificator'
  1.3.6.1.2.1.1.5.0 = 'Notificator Example'

Functionally similar to:

| $ snmptrap -v2c -c public udp:127.0.0.1 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s 'Example notification' 1.3.6.1.2.1.1.5.0 s 'Notificator Example'
| $ snmptrap -v2c -c public udp6:[::1] 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s 'Example notification' 1.3.6.1.2.1.1.5.0 s 'Notificator Example'

"""  #
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pysnmp.entity.rfc3413 import ntforg
from pysnmp.proto.api import v2c

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

# SecurityName <-> CommunityName mapping
config.add_v1_system(snmpEngine, "my-area", "public", transportTag="all-my-managers")

# Specify security settings per SecurityName (SNMPv2c -> 1)
config.add_target_parameters(snmpEngine, "my-creds", "my-area", "noAuthNoPriv", 1)

# Setup transport endpoints and bind it with security settings yielding
# a target name:

# UDP/IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_client_mode()
)
config.add_target_address(
    snmpEngine,
    "my-nms-1",
    udp.DOMAIN_NAME,
    ("127.0.0.1", 162),
    "my-creds",
    tagList="all-my-managers",
)

# UDP/IPv6
config.add_transport(
    snmpEngine, udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport().open_client_mode()
)
config.add_target_address(
    snmpEngine,
    "my-nms-2",
    udp6.DOMAIN_NAME,
    ("::1", 162),
    "my-creds",
    tagList="all-my-managers",
)

# Specify what kind of notification should be sent (TRAP or INFORM),
# to what targets (chosen by tag) and what filter should apply to
# the set of targets (selected by tag)
config.add_notification_target(
    snmpEngine, "my-notification", "my-filter", "all-my-managers", "trap"
)

# Allow NOTIFY access to Agent's MIB by this SNMP model (2), securityLevel
# and SecurityName
config.add_context(snmpEngine, "")
config.add_vacm_user(snmpEngine, 2, "my-area", "noAuthNoPriv", (), (), (1, 3, 6))

# *** SNMP engine configuration is complete by this line ***

# Create Notification Originator App instance.
ntfOrg = ntforg.NotificationOriginator()

# Build and submit notification message to dispatcher
ntfOrg.send_varbinds(
    snmpEngine,
    # Notification targets
    "my-notification",  # notification targets
    None,
    "",  # contextEngineId, contextName
    # var-binds
    [
        # SNMPv2-SMI::snmpTrapOID.0 = SNMPv2-MIB::coldStart
        (
            (1, 3, 6, 1, 6, 3, 1, 1, 4, 1, 0),
            v2c.ObjectIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 5, 1)),
        ),
        # additional var-binds: ( (oid, value), ... )
        ((1, 3, 6, 1, 2, 1, 1, 1, 0), v2c.OctetString("Example Notificator")),
        ((1, 3, 6, 1, 2, 1, 1, 5, 0), v2c.OctetString("Notificator Example")),
    ],
)

print("Notification is scheduled to be sent")

# Run I/O dispatcher which would send pending message and process response
snmpEngine.open_dispatcher()
