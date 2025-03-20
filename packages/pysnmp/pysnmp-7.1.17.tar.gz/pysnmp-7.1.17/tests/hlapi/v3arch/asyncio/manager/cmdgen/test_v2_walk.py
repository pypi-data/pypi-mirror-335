import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager

total_count = 212  # 267


@pytest.mark.asyncio
async def test_v2_walk():  # some agents have different v2 GET NEXT behavior
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        objects = walk_cmd(
            snmpEngine,
            CommunityData("public"),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        objects_list = [item async for item in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"

        assert len(objects_list) == total_count

        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2_walk_subtree():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        objects = walk_cmd(
            snmpEngine,
            CommunityData("public"),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
            lexicographicMode=False,
        )

        objects_list = [item async for item in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        assert len(objects_list) == 8

        snmpEngine.close_dispatcher()
