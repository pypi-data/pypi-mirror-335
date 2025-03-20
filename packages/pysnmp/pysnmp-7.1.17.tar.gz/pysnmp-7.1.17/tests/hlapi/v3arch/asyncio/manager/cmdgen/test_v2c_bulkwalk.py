import math
import pytest

from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager

total_count = 68  # Ensure this matches the actual total count of SNMP objects


@pytest.mark.asyncio
@pytest.mark.parametrize("max_repetitions", [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30])
async def test_v2c_get_table_bulk(max_repetitions):
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            ContextData(),
            0,
            max_repetitions,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

        assert len(objects_list) == math.ceil(total_count / max_repetitions)

        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_4_subtree():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        index = 0
        async for errorIndication, errorStatus, errorIndex, varBinds in bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            0,
            4,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
            lexicographicMode=False,
        ):
            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 4
            if index == 0:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpInPkts.0"

            if index == 1:
                assert (
                    varBinds[0][0].prettyPrint()
                    == "SNMPv2-MIB::snmpInBadCommunityUses.0"
                )

            if index == 26:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpSilentDrops.0"

            if index == 27:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpProxyDrops.0"

            index += 1

        assert index == 7

        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_1_subtree():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        index = 0
        async for errorIndication, errorStatus, errorIndex, varBinds in bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            0,
            1,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
            lexicographicMode=False,
        ):
            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            if index == 0:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpInPkts.0"

            if index == 1:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpOutPkts.0"

            if index == 26:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpSilentDrops.0"

            if index == 27:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpProxyDrops.0"

            index += 1

        assert index == 28

        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_7():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        max_repetitions = 7
        objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            ContextData(),
            0,
            max_repetitions,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

        assert len(objects_list) == math.ceil(total_count / max_repetitions)
        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_8():
    snmpEngine = SnmpEngine()
    max_repetitions = 8
    objects = bulk_walk_cmd(
        snmpEngine,
        CommunityData("public"),
        # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
        await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
        ContextData(),
        0,
        max_repetitions,
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    objects_list = [obj async for obj in objects]

    errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == max_repetitions
    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

    errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == max_repetitions
    # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

    assert len(objects_list) == math.ceil(total_count / max_repetitions)
    snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_35():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        max_repetitions = 35  # (68/2) + 1
        objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            ContextData(),
            0,
            max_repetitions,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == total_count - max_repetitions
        # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

        assert len(objects_list) == math.ceil(total_count / max_repetitions)
        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_60():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        max_repetitions = 60
        objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            ContextData(),
            0,
            max_repetitions,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        assert len(objects_list) == math.ceil(total_count / max_repetitions)
        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_5_subtree():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        max_repetitions = 5
        objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            ContextData(),
            0,
            max_repetitions,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
            lexicographicMode=False,
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[3]
        assert len(varBinds) == 1

        assert len(objects_list) == 4
        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_6_subtree():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        max_repetitions = 6
        objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            ContextData(),
            0,
            max_repetitions,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
            lexicographicMode=False,
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[2]
        assert len(varBinds) == 4

        assert len(objects_list) == 3
        snmpEngine.close_dispatcher()
