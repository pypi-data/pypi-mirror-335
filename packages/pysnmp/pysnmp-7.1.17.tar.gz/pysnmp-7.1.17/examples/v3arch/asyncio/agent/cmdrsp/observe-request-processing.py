"""
Observe SNMP engine operations
++++++++++++++++++++++++++++++

Listen and respond to SNMP GET/SET/GETNEXT/GETBULK queries with
the following options:

* SNMPv3
* with USM user 'usr-md5-des', auth: MD5, priv DES or
* allow access to SNMPv2-MIB objects (1.3.6.1.2.1)
* over IPv4/UDP, listening at 127.0.0.1:161
* registers its own execution observer to snmpEngine

The following Net-SNMP command will walk this Agent:

| $ snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost .1.3.6

This script will report some details on request processing as seen
by rfc3412.receiveMessage() and rfc3412.returnResponsePdu()
abstract interfaces.

"""  #
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp

# Create SNMP engine
snmpEngine = engine.SnmpEngine()


# Execution point observer setup


# Register a callback to be invoked at specified execution point of
# SNMP Engine and passed local variables at code point's local scope
# noinspection PyUnusedLocal,PyUnusedLocal
def requestObserver(snmpEngine, execpoint, variables, cbCtx):
    print("Execution point: %s" % execpoint)
    print(
        "* transportDomain: %s"
        % ".".join([str(x) for x in variables["transportDomain"]])
    )
    print(
        "* transportAddress: {} (local {})".format(
            "@".join([str(x) for x in variables["transportAddress"]]),
            "@".join([str(x) for x in variables["transportAddress"].getLocalAddress()]),
        )
    )
    print("* securityModel: %s" % variables["securityModel"])
    print("* securityName: %s" % variables["securityName"])
    print("* securityLevel: %s" % variables["securityLevel"])
    print("* contextEngineId: %s" % variables["contextEngineId"].prettyPrint())
    print("* contextName: %s" % variables["contextName"].prettyPrint())
    print("* PDU: %s" % variables["pdu"].prettyPrint())


snmpEngine.observer.register_observer(
    requestObserver, "rfc3412.receiveMessage:request", "rfc3412.returnResponsePdu"
)

# Transport setup

# UDP over IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpTransport().open_server_mode(("127.0.0.1", 161))
)

# SNMPv3/USM setup

# user: usr-md5-des, auth: MD5, priv DES
config.add_v3_user(
    snmpEngine,
    "usr-md5-des",
    config.USM_AUTH_HMAC96_MD5,
    "authkey1",
    config.USM_PRIV_CBC56_DES,
    "privkey1",
)

# Allow full MIB access for each user at VACM
config.add_vacm_user(
    snmpEngine, 3, "usr-md5-des", "authPriv", (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1)
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
    snmpEngine.observer.unregister_observer()
    snmpEngine.close_dispatcher()
    raise
