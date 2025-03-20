"""
Notification over multiple SNMP versions
++++++++++++++++++++++++++++++++++++++++

Send SNMP INFORM notifications to multiple Managers using different
security settings:

* SNMPv2c
* with community name 'public'
* AND
* SNMPv3
* with user 'usr-md5-none', auth: MD5, priv NONE
* over IPv4/UDP
* send INFORM notification
* to multiple Managers at 127.0.0.1:162, 127.0.0.1:162
* with TRAP ID 'coldStart' specified as an OID
* include managed objects information:
  1.3.6.1.2.1.1.1.0 = 'Example Notificator'

Functionally similar to:

| $ snmpinform -v3 -l authPriv -u usr-md5-none -A authkey1 127.0.0.1 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s 'Example notification'
| $ snmpinform -v2c -c public 127.0.0.1 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s 'Example notification'

"""  #
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import ntforg
from pysnmp.proto.api import v2c

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

# SNMPv2c:

# SecurityName <-> CommunityName mapping
config.add_v1_system(snmpEngine, "my-area", "public", transportTag="all-my-managers")

# Specify security settings per SecurityName (SNMPv2c -> 1)
config.add_target_parameters(snmpEngine, "my-creds-1", "my-area", "noAuthNoPriv", 1)

# SNMPv3:

config.add_v3_user(snmpEngine, "usr-md5-none", config.USM_AUTH_HMAC96_MD5, "authkey1")
config.add_target_parameters(snmpEngine, "my-creds-2", "usr-md5-none", "authNoPriv")

# Setup transport endpoint and bind it with security settings yielding
# a target name
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_client_mode()
)
# First target
config.add_target_address(
    snmpEngine,
    "my-nms-1",
    udp.DOMAIN_NAME,
    ("127.0.0.1", 162),
    "my-creds-1",
    tagList="all-my-managers",
)
# Second target
config.add_target_address(
    snmpEngine,
    "my-nms-2",
    udp.DOMAIN_NAME,
    ("127.0.0.1", 162),
    "my-creds-2",
    tagList="all-my-managers",
)

# Specify what kind of notification should be sent (TRAP or INFORM),
# to what targets (chosen by tag) and what filter should apply to
# the set of targets (selected by tag)
config.add_notification_target(
    snmpEngine, "my-notification", "my-filter", "all-my-managers", "inform"
)

# Allow NOTIFY access to Agent's MIB by this SNMP model (2&3), securityLevel
# and SecurityName
config.add_context(snmpEngine, "")
config.add_vacm_user(snmpEngine, 2, "my-area", "noAuthNoPriv", (), (), (1, 3, 6))
config.add_vacm_user(snmpEngine, 3, "usr-md5-none", "authNoPriv", (), (), (1, 3, 6))

# *** SNMP engine configuration is complete by this line ***

# Create Notification Originator App instance.
ntfOrg = ntforg.NotificationOriginator()


# Error/confirmation receiver
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(
    snmpEngine,
    sendRequestHandle,
    errorIndication,
    errorStatus,
    errorIndex,
    varBinds,
    cbCtx,
):
    print(
        "Notification {}, status - {}".format(
            sendRequestHandle, errorIndication and errorIndication or "delivered"
        )
    )


# Build and submit notification message to dispatcher
sendRequestHandle = ntfOrg.send_varbinds(
    snmpEngine,
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
    ],
    cbFun,
)

print("Notifications %s are scheduled to be sent" % sendRequestHandle)

# Run I/O dispatcher which would send pending message and process response
snmpEngine.open_dispatcher()
