from __future__ import annotations

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner


# -------------------------------------------------
# APB Driver
# -------------------------------------------------

class APBDriver:

    def __init__(self, dut):
        self.dut = dut

    async def write(self, addr, data):

        dut = self.dut

        dut.WADDR.value = addr
        dut.WDATA.value = data
        dut.WRITE_IN.value = 1
        dut.TRANSFER.value = 1

        await RisingEdge(dut.PCLK)

        dut.TRANSFER.value = 0

        while dut.PENABLE.value == 0:
            await RisingEdge(dut.PCLK)

        await RisingEdge(dut.PCLK)


    async def read(self, addr):

        dut = self.dut

        dut.WADDR.value = addr
        dut.WRITE_IN.value = 0
        dut.TRANSFER.value = 1

        await RisingEdge(dut.PCLK)

        dut.TRANSFER.value = 0

        while dut.PENABLE.value == 0:
            await RisingEdge(dut.PCLK)

        await RisingEdge(dut.PCLK)

        return dut.PRDATA.value.integer


# -------------------------------------------------
# Reset
# -------------------------------------------------

async def reset(dut):

    dut.PRESET_n.value = 0
    await RisingEdge(dut.PCLK)

    dut.PRESET_n.value = 1
    await RisingEdge(dut.PCLK)


# -------------------------------------------------
# Protocol Check
# -------------------------------------------------

async def protocol_check(dut, num_edges=10):

    prev_psel = 0

    for _ in range(num_edges):

        await RisingEdge(dut.PCLK)

        psel = int(dut.PSELx.value)
        penable = int(dut.PENABLE.value)

        if penable == 1 and psel == 0:
            raise AssertionError("APB protocol violation: PENABLE without PSELx")

        if penable == 1 and prev_psel == 0:
            raise AssertionError("APB protocol violation: ACCESS without SETUP")

        prev_psel = psel


# -------------------------------------------------
# Random Functional Test
# -------------------------------------------------

@cocotb.test()
async def apb_random_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    # Match golden apb_top REG_NUM=64, word-aligned addressing
    REG_NUM = 64
    model = [0] * REG_NUM

    for _ in range(10):

        addr = random.randint(0, 63) * 4  # word-aligned

        if random.random() < 0.5:

            data = random.randint(0, 0xffffffff)

            await driver.write(addr, data)

            model[(addr >> 2) % REG_NUM] = data

        else:

            val = await driver.read(addr)

            expected = model[(addr >> 2) % REG_NUM]

            assert val == expected, \
                f"Mismatch addr {addr}: got {val} expected {expected}"

    await protocol_check(dut, 8)


# -------------------------------------------------
# Back-to-back transfers
# -------------------------------------------------

@cocotb.test()
async def apb_back_to_back_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    for _ in range(8):

        addr = random.randint(0, 255)
        data = random.randint(0, 0xffffffff)

        await driver.write(addr, data)

        val = await driver.read(addr)

        assert val == data


# -------------------------------------------------
# PREADY wait test
# -------------------------------------------------

@cocotb.test()
async def apb_pready_wait_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    addr = random.randint(0, 255)
    data = random.randint(0, 0xffffffff)

    await driver.write(addr, data)

    val = await driver.read(addr)

    assert val == data


# -------------------------------------------------
# Reset value test
# -------------------------------------------------

@cocotb.test()
async def apb_reset_value_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    for addr in range(0, 16, 4):

        val = await driver.read(addr)

        assert val == 0, f"Register not reset at addr {addr}"


# -------------------------------------------------
# Full register sweep
# -------------------------------------------------

@cocotb.test()
async def apb_full_register_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    model = {}

    for addr in range(0, 64, 4):

        data = random.randint(0, 0xffffffff)

        await driver.write(addr, data)

        model[addr] = data

    for addr in range(0, 64, 4):

        val = await driver.read(addr)

        assert val == model[addr]


# -------------------------------------------------
# Overwrite test
# -------------------------------------------------

@cocotb.test()
async def apb_overwrite_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    addr = 0x10

    for _ in range(5):

        data = random.randint(0, 0xffffffff)

        await driver.write(addr, data)

        val = await driver.read(addr)

        assert val == data


# -------------------------------------------------
# Multiple read stability
# -------------------------------------------------

@cocotb.test()
async def apb_multiple_read_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    addr = 0x08
    data = random.randint(0, 0xffffffff)

    await driver.write(addr, data)

    for _ in range(5):

        val = await driver.read(addr)

        assert val == data


# -------------------------------------------------
# Address boundary test
# -------------------------------------------------

@cocotb.test()
async def apb_address_boundary_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    addresses = [0x00, 0x04, 0xFC, 0xFF]

    for addr in addresses:

        data = random.randint(0, 0xffffffff)

        await driver.write(addr, data)

        val = await driver.read(addr)

        assert val == data


# -------------------------------------------------
# Idle cycle test
# -------------------------------------------------

@cocotb.test()
async def apb_idle_cycle_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    for _ in range(5):

        addr = random.randint(0, 255)
        data = random.randint(0, 0xffffffff)

        await driver.write(addr, data)

        for _ in range(random.randint(1, 5)):
            await RisingEdge(dut.PCLK)

        val = await driver.read(addr)

        assert val == data


# -------------------------------------------------
# PSLVERR check
# -------------------------------------------------

@cocotb.test()
async def apb_pslverr_check(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    for _ in range(10):

        addr = random.randint(0, 255)

        if random.random() < 0.5:

            data = random.randint(0, 0xffffffff)

            await driver.write(addr, data)

        else:

            await driver.read(addr)

        assert int(dut.PSLVERR.value) == 0, "Unexpected PSLVERR detected"


# -------------------------------------------------
# Stress test
# -------------------------------------------------

@cocotb.test()
async def apb_stress_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    model = {}

    for _ in range(100):

        addr = random.randint(0, 63) * 4  # word-aligned to match slave

        if random.random() < 0.5:

            data = random.randint(0, 0xffffffff)

            await driver.write(addr, data)

            model[addr] = data

        else:

            val = await driver.read(addr)

            expected = model.get(addr, 0)

            assert val == expected


# -------------------------------------------------
# Runner
# -------------------------------------------------

def test_apb_runner():

    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [
        proj_path / "golden/apb_top.sv",
        proj_path / "golden/apb_master.sv",
        proj_path / "golden/apb_slave.sv",
    ]

    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel="apb_top",
        always=False,
    )

    runner.test(
        hdl_toplevel="apb_top",
        test_module="test_apb_rtl_hidden",
    )