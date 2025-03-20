import pytest
from pysnmp.hlapi.v1arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v2_get():
    async with AgentContextManager():
        snmpDispatcher = SnmpDispatcher()
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public"),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
        assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
        assert isinstance(varBinds[0][1], OctetString)

        snmpDispatcher.transport_dispatcher.close_dispatcher()


@pytest.mark.asyncio
async def test_v2_get_no_access_object():
    async with AgentContextManager(enable_custom_objects=True):
        snmpDispatcher = SnmpDispatcher()
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public"),
            await UdpTransportTarget.create(
                ("localhost", AGENT_PORT), timeout=1, retries=0
            ),
            ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.3")),
        )

        assert errorIndication is None
        assert errorStatus.prettyPrint() == "noAccess"  # v2c and v3 use noAccess
        snmpDispatcher.transport_dispatcher.close_dispatcher()


@pytest.mark.asyncio
async def test_v2_get_legacy_object():
    async with AgentContextManager(enable_custom_objects=True):
        snmpDispatcher = SnmpDispatcher()
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public"),
            await UdpTransportTarget.create(
                ("localhost", AGENT_PORT), timeout=1, retries=0
            ),
            ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.4")),
        )

        assert errorIndication is None
        assert (
            errorStatus.prettyPrint() == "noAccess"
        )  # PySMI <1.3.0 generates such objects
        snmpDispatcher.transport_dispatcher.close_dispatcher()
