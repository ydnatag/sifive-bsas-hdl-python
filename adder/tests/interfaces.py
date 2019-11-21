import cocotb
from cocotb.triggers import RisingEdge
from cocotb.drivers import BusDriver
import random


class AxiStreamDriver(BusDriver):
    _signals =['TVALID', 'TREADY', 'TLAST', 'TDATA']

    def __init__(self, entity, name, clock):
        BusDriver.__init__(self, entity, name, clock)
        self.clk = clock
        self.buffer = []

    def accepted(self):
        return self.bus.TVALID.value.integer == 1 and self.bus.TREADY.value.integer == 1

    @cocotb.coroutine
    def _send(self, *data):
        self.write(*data)
        self.bus.TVALID <= 1
        yield RisingEdge(self.clk)
        while not self.accepted():
            yield RisingEdge(self.clk)
        self.bus.TVALID <= 0

    @cocotb.coroutine
    def _recv(self):
        self.bus.TREADY <= 1
        yield RisingEdge(self.clk)
        while not self.accepted():
            yield RisingEdge(self.clk)
        self.bus.TREADY <= 0
        return self.read()

    @cocotb.coroutine
    def send(self, data):
        for d in data[:-1]:
            try:
                yield self._send(*d)
            except TypeError:
                yield self._send(d)
        self.bus.TLAST <= 1
        try:
            yield self._send(*data[-1])
        except TypeError:
            yield self._send(data[-1])
        self.bus.TLAST <= 0

    @cocotb.coroutine
    def recv(self):
        data = []
        while True:
            d = yield self._recv()
            data.append(d)
            if self.bus.TLAST.value.integer == 1:
                break
        return data

    def write(self, *data):
        self.bus.TDATA <= data[0]

    def read(self):
        data = self.bus.TDATA.value.integer
        return data

class AxiStreamDriverBurps(AxiStreamDriver):
    @cocotb.coroutine
    def _send(self, *data):
        clocks_to_wait = random.choice(5*[0]+3*[1]+2*[2]+2*[3])
        for _ in range(clocks_to_wait):
            yield RisingEdge(self.clk)
        yield AxiStreamDriver._send(self, *data)

    @cocotb.coroutine
    def _recv(self):
        clocks_to_wait = random.choice(5*[0]+3*[1]+2*[2]+2*[3])
        for _ in range(clocks_to_wait):
            yield RisingEdge(self.clk)
        data = yield AxiStreamDriver._recv(self)
        return data

