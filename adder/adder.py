from nmigen import *
from nmigen.cli import main
from nmigen.hdl.rec import Direction

class AxiStream(Record):
    def __init__(self, width, direction=None, name=None, fields=None):
        self.width = width
        self.DATA_FIELDS = [('TDATA', width)]
        if direction == 'sink':
            layout = [('TDATA', width, Direction.FANIN),
                      ('TVALID', 1, Direction.FANIN),
                      ('TREADY', 1, Direction.FANOUT),
                      ('TLAST', 1, Direction.FANIN)]
        elif direction == 'source':
            layout = [('TDATA', width, Direction.FANOUT),
                      ('TVALID', 1, Direction.FANOUT),
                      ('TREADY', 1, Direction.FANIN),
                      ('TLAST', 1, Direction.FANOUT)]
        Record.__init__(self, layout, name=name, fields=fields)
        self.data = self.TDATA
        self.valid = self.TVALID
        self.ready = self.TREADY
        self.last = self.TLAST

    def accepted(self):
        return (self.TVALID == 1) & (self.TREADY == 1)


class Adder(Elaboratable):
    def __init__(self, width, domain='comb', interface=None):
        self.width = width
        self.interface = interface
        if self.interface == None:
            self.a = Signal(width)
            self.b = Signal(width)
            self.r = Signal(width + 1)
            self.d = domain
        else:
            self.a = self.interface(width, 'sink', name='a')
            self.b = self.interface(width, 'sink', name='b')
            self.r = self.interface(width + 1, 'source', name='r')

    def elaborate(self, platform):
        m = Module()
        if self.interface == None:
            m.domain[self.d] += self.r.eq(self.a + self.b)
        else:
            comb = m.domain.comb
            sync = m.domain.sync
            comb += self.a.ready.eq(0)
            comb += self.b.ready.eq(0)

            output_available = (self.r.valid == 0) | self.r.accepted()
            input_ready = (self.a.valid == 1) & (self.b.valid == 1) &  output_available

            comb += self.a.ready.eq(input_ready)
            comb += self.b.ready.eq(input_ready)

            with m.If(self.a.accepted() | self.b.accepted()):
                sync += self.r.data.eq(self.a.data + self.b.data)
                sync += self.r.valid.eq(1)
                sync += self.r.last.eq(self.a.last | self.b.last)

            with m.Elif(self.r.accepted()):
                sync += self.r.data.eq(0)
                sync += self.r.valid.eq(0)
                sync += self.r.last.eq(0)
        return m

if __name__ == '__main__':
    m = Adder(10, 'sync', AxiStream)
    ports = []
    for i in [m.a, m.b, m.r]:
        ports += [i[f] for f in i.fields]
    main(m, platform=None, ports=ports)




