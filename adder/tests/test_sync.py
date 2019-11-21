from nmigen_cocotb import run
from adder.adder import Adder

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.coroutine
def init_test(dut):
    cocotb.fork(Clock(dut.clk, 10, 'ns').start())
    dut.rst <= 1
    dut.a <= 0
    dut.b <= 0
    yield RisingEdge(dut.clk)
    dut.rst <= 0
    yield RisingEdge(dut.clk)

@cocotb.test()
def data_check(dut):
    yield init_test(dut)

    outputs = []
    inputs = []
    for _ in range(random.randint(5, 10)):
        a = random.getrandbits(len(dut.a))
        b = random.getrandbits(len(dut.b))
        dut.a <= a
        dut.b <= b
        yield RisingEdge(dut.clk)
        inputs.append((a,b))
        outputs.append(dut.r.value.integer)
    yield RisingEdge(dut.clk)
    outputs.append(dut.r.value.integer)

    outputs = outputs[1::]
    for (a, b), r in zip(inputs, outputs):
        assert a+ b == r

def test_sync():
    m = Adder(10, 'sync')
    ports = [m.a, m.b, m.r]
    run(m, 'adder.tests.test_sync', ports=ports, vcd_file='sync.vcd')




