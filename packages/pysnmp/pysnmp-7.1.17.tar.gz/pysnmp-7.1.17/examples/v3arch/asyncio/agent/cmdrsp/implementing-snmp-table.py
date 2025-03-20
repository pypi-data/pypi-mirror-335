"""
Implementing conceptual table
+++++++++++++++++++++++++++++

Listen and respond to SNMP GET/SET/GETNEXT/GETBULK queries with
the following options:

* SNMPv2c
* with SNMP community "public"
* define a simple SNMP Table within a newly created EXAMPLE-MIB
* pre-populate SNMP Table with a single row of values
* allow read access only to the subtree where example SNMP Table resides
* over IPv4/UDP, listening at 127.0.0.1:161

The following Net-SNMP commands will populate and walk a table:

| $ snmpset -v2c -c public 127.0.0.1 1.3.6.6.1.5.2.97.98.99 s "my value"
| $ snmpset -v2c -c public 127.0.0.1 1.3.6.6.1.5.4.97.98.99 i 4
| $ snmpwalk -v2c -c public 127.0.0.1 1.3.6

...while the following command will destroy the same row

| $ snmpset -v2c -c public 127.0.0.1 1.3.6.6.1.5.4.97.98.99 i 6
| $ snmpwalk -v2c -c public 127.0.0.1 1.3.6

"""  #
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.proto.api import v2c


# Create SNMP engine
snmpEngine = engine.SnmpEngine()

# Transport setup

# UDP over IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpTransport().open_server_mode(("127.0.0.1", 161))
)

# SNMPv2c setup

# SecurityName <-> CommunityName mapping.
config.add_v1_system(snmpEngine, "my-area", "public")

# Allow read MIB access for this user / securityModels at VACM
config.add_vacm_user(
    snmpEngine, 2, "my-area", "noAuthNoPriv", (1, 3, 6, 6), (1, 3, 6, 6)
)

# Create an SNMP context
snmpContext = context.SnmpContext(snmpEngine)

# --- define custom SNMP Table within a newly defined EXAMPLE-MIB ---

mibBuilder = snmpContext.get_mib_instrum().get_mib_builder()

(MibTable, MibTableRow, MibTableColumn, MibScalarInstance) = mibBuilder.import_symbols(
    "SNMPv2-SMI", "MibTable", "MibTableRow", "MibTableColumn", "MibScalarInstance"
)

(RowStatus,) = mibBuilder.import_symbols("SNMPv2-TC", "RowStatus")

mibBuilder.export_symbols(
    "__EXAMPLE-MIB",
    # table object
    exampleTable=MibTable((1, 3, 6, 6, 1)).setMaxAccess("read-create"),
    # table row object, also carries references to table indices
    exampleTableEntry=MibTableRow((1, 3, 6, 6, 1, 5))
    .setMaxAccess("read-create")
    .setIndexNames((0, "__EXAMPLE-MIB", "exampleTableColumn1")),
    # table column: string index
    exampleTableColumn1=MibTableColumn(
        (1, 3, 6, 6, 1, 5, 1), v2c.OctetString()
    ).setMaxAccess("read-create"),
    # table column: string value
    exampleTableColumn2=MibTableColumn(
        (1, 3, 6, 6, 1, 5, 2), v2c.OctetString()
    ).setMaxAccess("read-create"),
    # table column: integer value with default
    exampleTableColumn3=MibTableColumn(
        (1, 3, 6, 6, 1, 5, 3), v2c.Integer32(123)
    ).setMaxAccess("read-create"),
    # table column: row status
    exampleTableStatus=MibTableColumn(
        (1, 3, 6, 6, 1, 5, 4), RowStatus("notExists")
    ).setMaxAccess("read-create"),
)

# --- end of custom SNMP table definition, empty table now exists ---

# --- populate custom SNMP table with one row ---

(
    exampleTableEntry,
    exampleTableColumn2,
    exampleTableColumn3,
    exampleTableStatus,
) = mibBuilder.import_symbols(
    "__EXAMPLE-MIB",
    "exampleTableEntry",
    "exampleTableColumn2",
    "exampleTableColumn3",
    "exampleTableStatus",
)
rowInstanceId = exampleTableEntry.getInstIdFromIndices("example record one")
mibInstrumentation = snmpContext.get_mib_instrum()
mibInstrumentation.write_variables(
    (exampleTableColumn2.name + rowInstanceId, "my string value"),
    (exampleTableColumn3.name + rowInstanceId, 123456),
    (exampleTableStatus.name + rowInstanceId, "createAndGo"),
)

# --- end of SNMP table population ---

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
