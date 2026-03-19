from __future__ import annotations

import os
import random
from pathlib import Path

import pytest
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner


random.seed(42)


def _logic_to_int(value):
    """Convert cocotb Logic/LogicArray/BinaryValue to int; treat X/Z as 0."""
    try:
        if hasattr(value, "to_unsigned"):
            return int(value.to_unsigned())
        if hasattr(value, "integer"):
            return int(value.integer)
        return int(value)
    except (ValueError, TypeError, AttributeError):
        return 0


# -------------------------------------------------
# APB Driver
# -------------------------------------------------

# Max cycles to wait for PREADY after ACCESS phase starts (per spec: transaction completes when PREADY=1).
PREADY_MAX_WAIT_CYCLES = 16


async def _wait_for_pready(dut, max_cycles=PREADY_MAX_WAIT_CYCLES):
    """Wait for PREADY to be 1 within N cycles (after ACCESS phase); raise AssertionError if not seen.
    Slave outputs PREADY/PRDATA on posedge, so we advance one cycle then poll for PREADY."""
    await RisingEdge(dut.PCLK)  # First cycle where slave can have driven PREADY after PENABLE=1
    for _ in range(max_cycles):
        if _logic_to_int(dut.PREADY.value) == 1:
            return
        await RisingEdge(dut.PCLK)
    raise AssertionError(f"PREADY did not become 1 within {max_cycles} cycles")


class APBDriver:

    def __init__(self, dut):
        self.dut = dut

    async def write(self, addr, data):
        """Drive test inputs (TRANSFER, WADDR, WDATA, WRITE_IN); DUT drives PSELx, PENABLE. Wait for PREADY within N cycles."""
        dut = self.dut
        dut.WADDR.value = addr
        dut.WDATA.value = data
        dut.WRITE_IN.value = 1
        dut.TRANSFER.value = 1
        await RisingEdge(dut.PCLK)
        dut.TRANSFER.value = 0
        while _logic_to_int(dut.PENABLE.value) == 0:
            await RisingEdge(dut.PCLK)
        await _wait_for_pready(dut)

    async def read(self, addr):
        """Drive test inputs; sample PRDATA when PREADY=1 (within N cycles)."""
        dut = self.dut
        dut.WADDR.value = addr
        dut.WRITE_IN.value = 0
        dut.TRANSFER.value = 1
        await RisingEdge(dut.PCLK)
        dut.TRANSFER.value = 0
        while _logic_to_int(dut.PENABLE.value) == 0:
            await RisingEdge(dut.PCLK)
        await _wait_for_pready(dut)
        return _logic_to_int(dut.PRDATA.value)


# -------------------------------------------------
# Reset
# -------------------------------------------------

async def reset(dut):

    dut.PRESETn.value = 0
    await RisingEdge(dut.PCLK)

    dut.PRESETn.value = 1
    await RisingEdge(dut.PCLK)


# -------------------------------------------------
# Random Functional Test
# -------------------------------------------------

#@cocotb.test()
#async def apb_random_test(dut):

#    cocotb.start_soon(Clock(dut.PCLK, 10, unit="ns").start())

    #await reset(dut)

    #driver = APBDriver(dut)

   # REG_NUM = 64
   # model = [0] * REG_NUM

  #  for _ in range(20):

  #      addr = random.randint(0, 63) * 4

   #     if random.random() < 0.5:

   #         data = random.randint(0, 0xffffffff)

    #        await driver.write(addr, data)

    #        model[(addr >> 2) % REG_NUM] = data

    #    else:

    #        val = await driver.read(addr)

     #       expected = model[(addr >> 2) % REG_NUM]

      #      assert val == expected, f"Mismatch addr {addr}: got {val} expected {expected}"


# -------------------------------------------------
# Back-to-back transfers
# -------------------------------------------------

@cocotb.test()
async def apb_back_to_back_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, unit="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    for _ in range(10):

        addr = random.randint(0, 63) * 4
        data = random.randint(0, 0xffffffff)

        await driver.write(addr, data)

        val = await driver.read(addr)

        assert val == data, f"Back-to-back mismatch addr {addr}"


# -------------------------------------------------
# Reset value test
# -------------------------------------------------

@cocotb.test()
async def apb_reset_value_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, unit="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    for addr in range(0, 64, 4):

        val = await driver.read(addr)

        assert val == 0, f"Register not reset at addr {addr}"


# -------------------------------------------------
# Full register sweep
# -------------------------------------------------
@cocotb.test()
async def apb_full_register_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, unit="ns").start())

    await reset(dut)

    driver = APBDriver(dut)

    model = {}

    for addr in range(0, 64, 4):

        data = random.randint(0, 0xffffffff)

        await driver.write(addr, data)

        model[addr] = data

    for addr in range(0, 64, 4):

        val = await driver.read(addr)

        assert val == model[addr], f"Register sweep mismatch at {addr}"


# -------------------------------------------------
# Stress test
# -------------------------------------------------

# @cocotb.test()
#async def apb_stress_test(dut):

 #   cocotb.start_soon(Clock(dut.PCLK, 10, unit="ns").start())

 #   await reset(dut)

 #   driver = APBDriver(dut)

 #   model = {}

 #   for _ in range(100):

 #       addr = random.randint(0, 63) * 4

 #       if random.random() < 0.5:

 #           data = random.randint(0, 0xffffffff)

 #           await driver.write(addr, data)

 #           model[addr] = data

 #       else:

 #           val = await driver.read(addr)

 #           expected = model.get(addr, 0)

   #         assert val == expected, f"Stress mismatch addr {addr}"#


# -------------------------------------------------
# Runner
# -------------------------------------------------

def test_apb_runner():

    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [
        proj_path / "sources/apb_top.sv",
        proj_path / "sources/apb_master.sv",
        proj_path / "sources/apb_slave.sv",
    ]

    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel="apb_top",
        always=True,  # always rebuild so sim.vvp matches current sources (avoids stale build hang)
    )

    runner.test(
        hdl_toplevel="apb_top",
        test_module="test_apb_rtl_hidden",
    )