import os
import amaranth as am
from amaranth.back import verilog
from amaranth.sim import Simulator


class PRN(am.Elaboratable):
    """
    PRN generator.

    Inputs:
        * io_in[0] is used for clock
        * io_in[1] is used for reset

    Outputs:
        * io_out[0] is the final stage of the G1 LFSR
        * io_out[1] is the final stage of the G2 LFSR
        * io_out[2..7] are PRN1 through PRN6
    """
    def __init__(self):
        self.io_in = am.Signal(8)
        self.io_out = am.Signal(8)

    def elaborate(self, platform):
        m = am.Module()

        # Set up clock domain from io_in[0] and reset from io_in[1].
        cd_sync = am.ClockDomain("sync")
        m.d.comb += cd_sync.clk.eq(self.io_in[0])
        m.d.comb += cd_sync.rst.eq(self.io_in[1])
        m.domains += cd_sync

        # G1 shift register.
        g1 = am.Signal(10, reset=-1)
        m.d.sync += g1.eq(am.Cat(g1[2] ^ g1[9], g1))
        m.d.comb += self.io_out[0].eq(g1[9])

        # G2 shift register.
        g2 = am.Signal(10, reset=-1)
        g2fb = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
        m.d.sync += g2.eq(am.Cat(g2fb, g2))
        m.d.comb += self.io_out[1].eq(g2[9])

        # Output PRNs 1..6 on the remaining outputs.
        prns = ((2, 6), (3, 7), (4, 8), (5, 9), (1, 9), (2, 10))
        for i, (t1, t2) in enumerate(prns):
            m.d.comb += self.io_out[i+2].eq(g2[t1 - 1] ^ g2[t2 - 1] ^ g1[9])

        return m


def test():
    """
    Testcase for PRN generator.

    Run using `pytest tinytapeout_prn.py`.
    """
    prn = PRN()

    def testbench():
        # Trigger reset
        yield prn.io_in[1].eq(1)
        yield
        yield prn.io_in[1].eq(0)
        yield

        # Collect 20 output bits
        prns = [[], [], [], [], [], []]
        for _ in range(20):
            for i in range(len(prns)):
                prns[i].append((yield prn.io_out[i+2]))
            yield

        # Test PRN2 has the first 20 bits correct.
        assert prns[1][:20] == [
            1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1]

    sim = Simulator(prn)
    sim.add_clock(1/10e6)
    sim.add_sync_process(testbench)
    sim.run()


if __name__ == "__main__":
    # Generate Verilog source for PRN.
    # Note it's _not_ flattened, so avoid using submodules for now.
    prj_id = os.environ.get("WOKWI_PROJECT_ID", "WOKWI")
    prn = PRN()
    v = verilog.convert(
        prn, name=f"user_module_{prj_id}", ports=[prn.io_out, prn.io_in],
        emit_src=False, strip_internal_attrs=True)
    print(v)
