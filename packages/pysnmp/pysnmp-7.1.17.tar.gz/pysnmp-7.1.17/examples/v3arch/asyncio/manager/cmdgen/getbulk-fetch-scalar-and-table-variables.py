"""
Fetch scalar and table variables
++++++++++++++++++++++++++++++++

Send a series of SNMP GETBULK requests with the following options:

* with SNMPv3 with user 'usr-md5-des', MD5 auth and DES privacy protocols
* over IPv4/UDP
* to an Agent at 127.0.0.1:161
* with values non-repeaters = 1, max-repetitions = 25
* for two OIDs in tuple form (first OID is non-repeating)
* stop on end-of-mib condition for both OIDs

This script performs similar to the following Net-SNMP command:

| $ snmpbulkwalk -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 -C n1 -C r25 -ObentU 127.0.0.1 1.3.6.1.2.1.1 1.3.6.1.4.1.1

"""  #
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.carrier.asyncio.dgram import udp

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv3/USM setup
#

# user: usr-md5-des, auth: MD5, priv DES
config.add_v3_user(
    snmpEngine,
    "usr-md5-des",
    config.USM_AUTH_HMAC96_MD5,
    "authkey1",
    config.USM_PRIV_CBC56_DES,
    "privkey1",
)
config.add_target_parameters(snmpEngine, "my-creds", "usr-md5-des", "authPriv")

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
    sendRequesthandle,
    errorIndication,
    errorStatus,
    errorIndex,
    varBindTable,
    cbCtx,
):
    if errorIndication:
        print(errorIndication)
        return  # stop on error
    if errorStatus:
        print(
            f"{errorStatus.prettyPrint()} at {varBindTable[-1][int(errorIndex) - 1][0] if errorIndex else '?'}"
        )
        return  # stop on error
    for varBindRow in varBindTable:
        for oid, val in varBindRow:
            print(f"{oid.prettyPrint()} = {val.prettyPrint()}")
    return True  # signal dispatcher to continue walking


# Prepare initial request to be sent
cmdgen.BulkCommandGenerator().send_varbinds(
    snmpEngine,
    "my-router",
    None,
    "",  # contextEngineId, contextName
    0,
    25,  # non-repeaters, max-repetitions
    (((1, 3, 6, 1, 2, 1, 1), None), ((1, 3, 6, 1, 4, 1, 1), None)),
    cbFun,
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.oepn_dispatcher(3)

snmpEngine.close_dispatcher()
