import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.regression import TestFactory as TF
from nmigen_cocotb import run
from adder.adder import Adder, AxiStream
from .interfaces import *

@cocotb.coroutine
def init_test(dut):
    dut.a__TVALID <= 0
    dut.a__TDATA <= 0
    dut.a__TLAST <= 0
    dut.b__TVALID <= 0
    dut.b__TDATA <= 0
    dut.b__TLAST <= 0
    dut.r__TREADY <= 0
    dut.rst <= 1
    cocotb.fork(Clock(dut.clk, 10, 'ns').start())
    yield RisingEdge(dut.clk)
    dut.rst <= 0
    yield RisingEdge(dut.clk)

@cocotb.coroutine
def data_check(dut, driver):
    yield init_test(dut)
    a_stream = driver(dut, 'a_', dut.clk)
    b_stream = driver(dut, 'b_', dut.clk)
    r_stream = driver(dut, 'r_', dut.clk)

    a_width = len(a_stream.bus.TDATA)
    b_width = len(a_stream.bus.TDATA)

    a_data = [random.getrandbits(a_width) for _ in range(20)]
    b_data = [random.getrandbits(b_width) for _ in range(20)]
    cocotb.fork(a_stream.send(a_data))
    cocotb.fork(b_stream.send(b_data))

    r_data = yield r_stream.recv()
    for a, b, r in zip(a_data, b_data, r_data):
        assert a + b == r

tf_random_len = TF(data_check)
tf_random_len.add_option('driver', [AxiStreamDriver, AxiStreamDriverBurps])
tf_random_len.generate_tests()

def test_axis():
    m = Adder(10, 'sync', AxiStream)
    ports = []
    for i in [m.a, m.b, m.r]:
        ports += [i[f] for f in i.fields]
    run(m, 'adder.tests.test_axis', ports=ports, vcd_file='axis.vcd')
