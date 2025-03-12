import m5
from m5.objects import *
m5.util.addToPath("../../")
# from common import SimpleOpts


class L1Cache_ID(Cache):
    # Default parameters
    size = "256KiB"
    assoc = 1
    tag_latency = 1
    data_latency = 1
    response_latency = 1

    mshrs = 20
    tgts_per_mshr = 12

    # write_buffers = 8
    writeback_clean = True
    
    def __init__(self):
        super().__init__()
        pass
    
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port
        pass

    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports
        pass

class L1ICache(Cache):
    # Default parameters
    size = "64KiB"
    assoc = 2
    tag_latency = 1
    data_latency = 1
    response_latency = 1

    mshrs = 20
    tgts_per_mshr = 12

    # write_buffers = 8
    writeback_clean = True

    def __init__(self):
        super().__init__()
        pass
    
    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port
        pass

    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports
        pass

class L1DCache(Cache):
    # Default parameters
    size = "256KiB"
    assoc = 2
    tag_latency = 1
    data_latency = 1
    response_latency = 1

    mshrs = 20
    tgts_per_mshr = 12
    
    # write_buffers = 8
    writeback_clean = True

    def __init__(self):
        super().__init__()
        pass
    
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port
        pass
    
    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports
        pass
    
class L2Cache(Cache):
    # Default parameters
    size = "4MiB"
    assoc = 4
    tag_latency = 10
    data_latency = 10
    response_latency = 10
    mshrs = 100
    tgts_per_mshr = 12

    def __init__(self):
        super().__init__()
        pass

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports
        pass

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports
        pass

def main():

    L1_use_share = False
    L2_mode = True

    # create a system
    system = System()

    # Set the clock frequency of the system (and all of its children)
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = "1GHz"
    system.clk_domain.voltage_domain = VoltageDomain()

    # Set up the system
    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange("4GiB")]

    # Create a simple X86 CPU
    system.cpu = X86TimingSimpleCPU()

    # Create a memory bus
    system.membus = SystemXBar()

    # create the interrupt controller for the CPU
    system.cpu.createInterruptController()
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports


    # Connect the system up to the membus
    system.system_port = system.membus.cpu_side_ports

    # Create a DDR3 memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports
    
    # Set cache block size
    system.cache_line_size = 32

    # Choose Cache mode
    # shared L1
    if L1_use_share:
        print("Using Shared L1 Cache")

        l1_cache = L1Cache_ID()

        # Could work
        system.l1cache = l1_cache
        system.cache_bus = L2XBar()
        system.cpu.icache_port = system.cache_bus.cpu_side_ports
        system.cpu.dcache_port = system.cache_bus.cpu_side_ports
        system.cache_bus.mem_side_ports = system.l1cache.cpu_side
        system.l1cache.mem_side = system.membus.cpu_side_ports

        # Cannot work
        # system.cpu.icache = l1_cache
        # system.cpu.dcache = l1_cache
        # system.cpu.icache.cpu_side = system.cpu.icache_port
        # system.cpu.dcache.cpu_side = system.cpu.dcache_port
        # system.cpu.icache.mem_side = system.membus.cpu_side_ports
        # system.cpu.dcache.mem_side = system.membus.cpu_side_ports

    # Separate, No Problem
    elif (not L1_use_share) and (not L2_mode):
        print("Using Separate L1 Cache")
        system.cpu.icache = L1ICache()
        system.cpu.dcache = L1DCache()

        system.cpu.icache.connectCPU(system.cpu)
        system.cpu.dcache.connectCPU(system.cpu)

        system.cpu.icache.connectBus(system.membus)
        system.cpu.dcache.connectBus(system.membus)

    # L1 & L2, No Problem
    elif(not L1_use_share) and L2_mode:
        print("Using L1 and L2 Cache")

        system.cpu.icache = L1ICache()
        system.cpu.dcache = L1DCache()

        system.cpu.icache.connectCPU(system.cpu)
        system.cpu.dcache.connectCPU(system.cpu)

        # Create a memory bus, a coherent crossbar, in this case
        system.l2bus = L2XBar()
        
        # Hook the CPU ports up to the l2bus
        system.cpu.icache.connectBus(system.l2bus)
        system.cpu.dcache.connectBus(system.l2bus)

        # Create an L2 cache and connect it to the l2bus
        system.l2cache = L2Cache()
        system.l2cache.connectCPUSideBus(system.l2bus)

        # Connect the L2 cache to the membus
        system.l2cache.connectMemSideBus(system.membus)
    
    else:
        assert ("No Config")
    
    # workload
    system.workload = SEWorkload.init_compatible("./mat-mult")
    process = Process()
    process.cmd = ['./mat-mult']
    system.cpu.workload = process
    system.cpu.createThreads()

    # Init
    root = Root(full_system=False, system=system)
    m5.instantiate()

    # Run
    print(f"Beginning simulation!")
    exit_event = m5.simulate()
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

main()