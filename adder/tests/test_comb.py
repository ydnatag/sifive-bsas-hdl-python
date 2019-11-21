from nmigen_cocotb import run
from adder.adder import Adder

import random

import cocotb
from cocotb.triggers import Timer

@cocotb.test()
def data_check(dut):
    res = []
    for _ in range(random.randint(5, 100)):
        a = random.getrandbits(len(dut.a))
        b = random.getrandbits(len(dut.b))
        dut.a <= a
        dut.b <= b
        yield Timer(1, 'ns')
        res.append((a, b, dut.r.value.integer))
    for r in res:
        assert r[0] + r[1] == r[2]

def test_comb():
    m = Adder(10, 'comb')
    ports = [m.a, m.b, m.r]
    run(m, 'adder.tests.test_comb', ports=ports, vcd_file='comb.vcd')




