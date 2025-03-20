"""
Walk Agent over IPv6
++++++++++++++++++++

Send a series of SNMP GETNEXT requests with the following options:

* with SNMPv3 with user 'usr-md5-none', MD5 auth and no privacy protocols
* over IPv6/UDP
* to an Agent at [::1]:161
* for two OIDs in tuple form
* stop on end-of-mib condition for both OIDs

This script performs similar to the following Net-SNMP command:

| $ snmpwalk -v3 -l authNoPriv -u usr-md5-none -A authkey1 -ObentU udp6:[::1]:161 1.3.6.1.2.1.1 1.3.6.1.4.1.1

"""  #
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp6
from pysnmp.entity.rfc3413 import cmdgen

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv3/USM setup
#

# user: usr-md5-des, auth: MD5, priv NONE
config.add_v3_user(snmpEngine, "usr-md5-none", config.USM_AUTH_HMAC96_MD5, "authkey1")
config.add_target_parameters(snmpEngine, "my-creds", "usr-md5-none", "authNoPriv")

#
# Setup transport endpoint and bind it with security settings yielding
# a target name
#

# UDP/IPv6
config.add_transport(
    snmpEngine, udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport().open_client_mode()
)
config.add_target_address(
    snmpEngine, "my-router", udp6.DOMAIN_NAME, ("::1", 161), "my-creds"
)


# Error/response receiver
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(
    snmpEngine,
    sendRequestHandle,
    errorIndication,
    errorStatus,
    errorIndex,
    varBindTable,
    cbCtx,
):
    if errorIndication:
        print(errorIndication)
        return
    if errorStatus:
        print(
            f"{errorStatus.prettyPrint()} at {varBindTable[-1][int(errorIndex) - 1][0] or '?'}"
        )
        return  # stop on error
    for varBindRow in varBindTable:
        for oid, val in varBindRow:
            print(f"{oid.prettyPrint()} = {val.prettyPrint()}")
    return True  # signal dispatcher to continue


# Prepare initial request to be sent
cmdgen.NextCommandGenerator().send_varbinds(
    snmpEngine,
    "my-router",
    None,
    "",  # contextEngineId, contextName
    [((1, 3, 6, 1, 2, 1, 1), None), ((1, 3, 6, 1, 4, 1, 1), None)],
    cbFun,
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.oepn_dispatcher(3)

snmpEngine.close_dispatcher()
