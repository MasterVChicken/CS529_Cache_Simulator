from Write_back_with_victim import WriteBackCache, CacheBlock,VictimCache
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(trace, item_sets, L1H=1, L2H=10, victimH = 5, L2M=100):
    print ("Simulate L1 and L2 Caches")
    res = []
    for item in item_sets:
        victim_cache = VictimCache(item)
        L2 = WriteBackCache(total_size=16384, block_size=128, associativity=16, victim_cache=victim_cache)
        L1_instr_cache = WriteBackCache(total_size=1024, block_size=32, associativity=2, lower_level_cache=L2)
        L1_data_cache = WriteBackCache(total_size=1024, block_size=32, associativity=2, lower_level_cache= L2)

        for op, address in trace:
            # instr read
            if op == 0:
                L1_data_cache.read(address)
            elif op == 1:
                L1_instr_cache.read(address)
            else: 
                L1_data_cache.write(address)
                L1_instr_cache.write(address)

        instr_access = (L1_instr_cache.read_misses+L1_instr_cache.write_misses) + (L1_instr_cache.read_hits+L1_instr_cache.write_hits)
        data_access = (L1_data_cache.read_misses+L1_data_cache.write_misses) + (L1_data_cache.read_hits+L1_data_cache.write_hits)

        instr_hit_rate = (L1_instr_cache.read_hits+L1_instr_cache.write_hits) / (instr_access)
        data_hit_rate = (L1_data_cache.read_hits+L1_data_cache.write_hits) / (data_access)

        L2_access = (L2.read_misses+L2.write_misses) + (L2.read_hits+L2.write_hits)
        L2_hit_rate = (L2.read_hits+L2.write_hits) / (L2_access)
        
        L1_miss_rate = ((L1_instr_cache.read_misses+L1_instr_cache.write_misses) + \
                        (L1_data_cache.read_misses+L1_data_cache.write_misses)) / (instr_access+data_access)
        
        L2_miss_rate = (L2.read_misses+L2.write_misses) / L2_access

        # AMAT = L1H + L1_miss_rate*(L2H + L2_miss_rate * L2M)

        # res.append([item, instr_access, (L1_instr_cache.read_misses+L1_instr_cache.write_misses), instr_hit_rate, \
        #             data_access, (L1_data_cache.read_misses+L1_data_cache.write_misses), data_hit_rate, \
        #             L2_access, (L2.write_misses + L2.read_misses), L2_hit_rate, AMAT])

        victim_access = (victim_cache.miss) + (victim_cache.hits)
        victim_miss_rate = (victim_cache.miss) / victim_access
        victim_hit_rate = (victim_cache.hits) / victim_access

        AMAT = L1H + L1_miss_rate*(L2H + L2_miss_rate * (victimH + victim_miss_rate * L2M))

        res.append([item, instr_access, (L1_instr_cache.read_misses+L1_instr_cache.write_misses), instr_hit_rate, \
                    data_access, (L1_data_cache.read_misses+L1_data_cache.write_misses), data_hit_rate, \
                    L2_access, (L2.write_misses + L2.read_misses), L2_hit_rate, \
                    victim_access, victim_cache.miss, victim_hit_rate, AMAT])

    return res


def simulate_cycles(trace, cycles):
    print ("Simulate L1 and L2 Caches")
    res = []
    for i, item in enumerate(cycles):
        victim_cache = VictimCache(size=8)
        L2 = WriteBackCache(total_size=16384, block_size=128, associativity=16, victim_cache=victim_cache)
        L1_instr_cache = WriteBackCache(total_size=1024, block_size=32, associativity=2, lower_level_cache=L2)
        L1_data_cache = WriteBackCache(total_size=1024, block_size=32, associativity=2, lower_level_cache= L2)

        for op, address in trace:
            # instr read
            if op == 0:
                L1_data_cache.read(address)
            elif op == 1:
                L1_instr_cache.read(address)
            else: 
                L1_data_cache.write(address)
                L1_instr_cache.write(address)

        instr_access = (L1_instr_cache.read_misses+L1_instr_cache.write_misses) + (L1_instr_cache.read_hits+L1_instr_cache.write_hits)
        data_access = (L1_data_cache.read_misses+L1_data_cache.write_misses) + (L1_data_cache.read_hits+L1_data_cache.write_hits)

        instr_hit_rate = (L1_instr_cache.read_hits+L1_instr_cache.write_hits) / (instr_access)
        data_hit_rate = (L1_data_cache.read_hits+L1_data_cache.write_hits) / (data_access)

        L2_access = (L2.read_misses+L2.write_misses) + (L2.read_hits+L2.write_hits)
        L2_hit_rate = (L2.read_hits+L2.write_hits) / (L2_access)
        
        L1_miss_rate = ((L1_instr_cache.read_misses+L1_instr_cache.write_misses) + \
                        (L1_data_cache.read_misses+L1_data_cache.write_misses)) / (instr_access+data_access)
        
        L2_miss_rate = (L2.read_misses+L2.write_misses) / L2_access

        # AMAT = L1H + L1_miss_rate*(L2H + L2_miss_rate * L2M)

        # res.append([item, instr_access, (L1_instr_cache.read_misses+L1_instr_cache.write_misses), instr_hit_rate, \
        #             data_access, (L1_data_cache.read_misses+L1_data_cache.write_misses), data_hit_rate, \
        #             L2_access, (L2.write_misses + L2.read_misses), L2_hit_rate, AMAT])

        victim_access = (victim_cache.miss) + (victim_cache.hits)
        victim_miss_rate = (victim_cache.miss) / victim_access
        victim_hit_rate = (victim_cache.hits) / victim_access

        L1H = item[0]
        L2H = item[1]
        victimH = item[2]
        L2M = 100

        AMAT = L1H + L1_miss_rate*(L2H + L2_miss_rate * (victimH + victim_miss_rate * L2M))

        res.append([item, instr_access, (L1_instr_cache.read_misses+L1_instr_cache.write_misses), instr_hit_rate, \
                    data_access, (L1_data_cache.read_misses+L1_data_cache.write_misses), data_hit_rate, \
                    L2_access, (L2.write_misses + L2.read_misses), L2_hit_rate, \
                    victim_access, victim_cache.miss, victim_hit_rate, AMAT])

    return res


def avg_records(res, num_test, num_item):
    for i in range(1,3):
        for z in range(num_test):
            for j in range(1,num_item):
                res[0][z][j] += res[i][z][j]
    
    for j in range(num_test):
        for i in range(1,num_item):
            res[0][j][i] /= 3
    
    return res[0]


def AMAT_fig_line(data, x_label, fp):
    fig, ax1 = plt.subplots()

    plt.title("AMAT")
    
    ax1.plot(data["Item"], data["AMAT"], 'o', ls='-', color="blue", label='AMAT')
    ax1.set_ylabel('Time')
    ax1.set_xlabel(x_label)
    
    fig.set_size_inches(8,6, forward=True)


    plt.savefig(f"./figures/{fp}/AMAT_cache_size.jpg", dpi = 150)


def AMAT_fig_bar(data, x_label, fp):
    fig, ax1 = plt.subplots()

    plt.title("AMAT")
    
    x = np.array(data["Item"].astype(str))
    y = np.array(data["AMAT"])

    ax1.bar(x, y)
    ax1.set_ylabel('Time')
    ax1.set_xlabel(x_label)
    
    fig.set_size_inches(8,6, forward=True)


    plt.savefig(f"./figures/{fp}/AMAT_cycles.jpg", dpi = 150)

def form_data_frame(ls):
    data = pd.DataFrame(ls)
    data.columns = ['Item', 'L1I_accesses', 'L1I_misses', 'L1I_hit_rate', 'L1D_accesses', 'L1D_misses', \
                         'L1D_hit_rate', 'L2_accesses', 'L2_misses', 'L2_hit_rate', \
                         'victim_access', 'victim_misses','victim_hit_rate', 'AMAT']
    
    print(data)

    return data



def main():
    file_list = ["./traces/cc.trace", "./traces/spice.trace", "./traces/tex.trace"]
    # file_list = ["./traces/tex.trace"]
    resL1L2 = []
    res_cycles = []

    for i, file in enumerate(file_list):
        f = open(file, 'r')
        trace = []
        for line in f:
            str = line.split(" ")
            trace.append((int(str[0]), int(str[1][:-1],16)))
        f.close()

        # associativities = [1, 2, 4, 8, 16, 32, 64, 128]

        cache_size = [2, 4, 8, 16, 32]
        resL1L2.append(simulate(trace, cache_size))

        cycles = [
            (1, 5, 2),
            (2, 10, 5),
            (1, 15, 10)
        ]
        res_cycles.append(simulate_cycles(trace, cycles))

    resL1L2 = avg_records(resL1L2, 5, 13)
    res_cycles = avg_records(res_cycles, 3, 13)


    print("different cache size: ", resL1L2)
    print("---------------------------------------------")
    print("different cycles: ", res_cycles)

    print("Figures")

    fp = "victim"
    
    x_label = "cache size"
    data_cache = form_data_frame(resL1L2)
    AMAT_fig_line(data_cache, x_label, fp)

    x_label = "cycles settings (L1H, L2H, victimH)"
    data_cycle = form_data_frame(res_cycles)
    AMAT_fig_bar(data_cycle,x_label,fp)


main()