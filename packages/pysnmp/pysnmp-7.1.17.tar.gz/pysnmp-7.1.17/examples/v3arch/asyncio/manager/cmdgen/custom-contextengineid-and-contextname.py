"""
Custom ContextEngineId and ContextName
++++++++++++++++++++++++++++++++++++++

Send a SNMP GET request with the following options:

* with SNMPv3 with user 'usr-md5-none', SHA auth and no privacy protocols
* for MIB instance identified by
* contextEngineId: 0x80004fb805636c6f75644dab22cc,
* contextName: da761cfc8c94d3aceef4f60f049105ba
* over IPv4/UDP
* to an Agent at 127.0.0.1:161
* for an OID in tuple form

This script performs similar to the following Net-SNMP command:

| $ snmpget -v3 -l authNoPriv -u usr-md5-none -A authkey1 -E 80004fb805636c6f75644dab22cc -n da761cfc8c94d3aceef4f60f049105ba -ObentU 127.0.0.1:161  1.3.6.1.2.1.1.1.0

"""  #
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.proto import rfc1902

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv3/USM setup
#

# user: usr-md5-none, auth: MD5, priv: NONE
config.add_v3_user(snmpEngine, "usr-md5-none", config.USM_AUTH_HMAC96_MD5, "authkey1")
config.add_target_parameters(snmpEngine, "my-creds", "usr-md5-none", "authNoPriv")

#
# Setup transport endpoint and bind it with security settings yielding
# a target name
#

# UDP/IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_client_mode()
)
config.add_target_address(
    snmpEngine, "my-router", udp.DOMAIN_NAME, ("127.0.0.1", 161), "my-creds"
)


# Error/response receiver
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(
    snmpEngine,
    sendRequestHandle,
    errorIndication,
    errorStatus,
    errorIndex,
    varBinds,
    cbCtx,
):
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print(
            f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1][0] if errorIndex else '?'}"
        )
    else:
        for oid, val in varBinds:
            print(f"{oid.prettyPrint()} = {val.prettyPrint()}")


# Prepare and send a request message, pass custom ContextEngineId & ContextName
cmdgen.GetCommandGenerator().send_varbinds(
    snmpEngine,
    "my-router",
    # contextEngineId
    rfc1902.OctetString(hexValue="80004fb805636c6f75644dab22cc"),
    # contextName
    rfc1902.OctetString("da761cfc8c94d3aceef4f60f049105ba"),
    [((1, 3, 6, 1, 2, 1, 1, 1, 0), None)],
    cbFun,
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.oepn_dispatcher(3)

snmpEngine.close_dispatcher()
