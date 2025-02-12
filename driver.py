from write_through_cache import CacheBlock, WriteThourghCache
from Write_back_Cache import CacheBlock, WriteBackCache

def simulate_write_through_caches(trace, associativities, hit_time=1, miss_penalty=100):
    print ("Simulate Write Throught Caches")
    res = []
    for assoc in associativities:
        instr_cache = WriteThourghCache(total_size=1024, block_size=32, associativity=assoc)
        data_cache = WriteThourghCache(total_size=1024, block_size=32, associativity=assoc)

        for op, address in trace:
            # instr read
            if op == 0:
                data_cache.read(address)
            elif op == 1:
                instr_cache.read(address)
            else:
                data_cache.write(address)
                instr_cache.write(address)


        instr_access = instr_cache.miss + instr_cache.hits
        data_access = data_cache.miss + data_cache.hits

        instr_hit_rate = instr_cache.hits / (instr_cache.miss + instr_cache.hits)
        data_hit_rate = data_cache.hits / (data_cache.miss + data_cache.hits)

        miss_rate = (instr_cache.miss+data_cache.miss) / (instr_access+data_access)

        AMAT = hit_time + (miss_rate * miss_penalty)

        res.append([assoc, instr_access, instr_cache.miss, data_access, data_cache.miss, instr_hit_rate, data_hit_rate, AMAT])

    return res

def simulate_write_back_caches(trace, associativities, hit_time=1, miss_penalty=100):
    print ("Simulate Write Back Caches")
    res = []
    for assoc in associativities:
        instr_cache = WriteBackCache(total_size=1024, block_size=32, associativity=assoc)
        data_cache = WriteBackCache(total_size=1024, block_size=32, associativity=assoc)

        for op, address in trace:
            # instr read
            if op == 0:
                data_cache.read(address)
            elif op == 1:
                instr_cache.read(address)
            else:
                data_cache.write(address)
                instr_cache.write(address)

        instr_access = (instr_cache.read_misses+instr_cache.write_misses) + (instr_cache.read_hits+instr_cache.write_hits)
        data_access = (data_cache.read_misses+data_cache.write_misses) + (data_cache.read_hits+data_cache.write_hits)

        instr_hit_rate = (instr_cache.read_hits+instr_cache.write_hits) / (instr_access)
        data_hit_rate = (data_cache.read_hits+data_cache.write_hits) / (data_access)

        miss_rate = ((instr_cache.read_misses+instr_cache.write_misses) + (data_cache.read_misses+data_cache.write_misses)) / (instr_access+data_access)

        AMAT = hit_time + (miss_rate * miss_penalty)

        res.append([assoc, instr_access, (instr_cache.read_misses+instr_cache.write_misses), \
                    data_access, (data_cache.read_misses+data_cache.write_misses), \
                    instr_hit_rate, data_hit_rate, AMAT])

    return res

def simulate_L1_L2(trace, associativities, L1H=1, L2H=10,L2M=100):
    print ("Simulate L1 and L2 Caches")
    res = []
    for assoc in associativities:
        L2 = WriteBackCache(total_size=16384, block_size=128, associativity=assoc)
        L1_instr_cache = WriteBackCache(total_size=1024, block_size=32, associativity=2, lower_level_cache=L2)
        L1_data_cache = WriteBackCache(total_size=1024, block_size=32, associativity=2, lower_level_cache=L2)

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

        AMAT = L1H + L1_miss_rate*(L2H + L2_miss_rate * L2M)

        res.append([assoc, instr_access, (L1_instr_cache.read_misses+L1_instr_cache.write_misses), instr_hit_rate, \
                    data_access, (L1_data_cache.read_misses+L1_data_cache.write_misses), data_hit_rate, \
                    L2_access, (L2.write_misses + L2.read_misses), L2_hit_rate, AMAT])

    return res

def avg_records(res, num_test, num_item):
    for i in range(1,3):
        for z in range(num_test):
            for j in range(1,num_item):
                res[0][z][j] += res[i][z][j]
    
    for j in range(num_test):
        for i in range(1,num_test):
            res[0][j][i] /= 3
    
    return res[0]
    

def main():
    file_list = ["./traces/cc.trace", "./traces/spice.trace", "./traces/tex.trace"]
    # file_list = ["./traces/tex.trace"]
    resWT = []
    resWB = []
    resL1L2 = []

    for file in file_list:
        f = open(file, 'r')
        trace = []
        for line in f:
            str = line.split(" ")
            trace.append((int(str[0]), int(str[1][:-1],16)))
        f.close()

        associativities = [1, 2, 4, 8, 16, 32]
        resWT.append(simulate_write_through_caches(trace, associativities))
        resWB.append(simulate_write_back_caches(trace, associativities))

        associativities = [1, 2, 4, 8, 16, 32, 64, 128]
        resL1L2.append(simulate_L1_L2(trace, associativities))

    resWT = avg_records(resWT, 6, 8)
    resWB = avg_records(resWB, 6, 8)
    resL1L2 = avg_records(resL1L2,8, 10)


    print("avg WT: ", resWT)
    print("------------------------------------------------------")
    print("avg WB: ", resWB)
    print("------------------------------------------------------")
    print("avg L1L2: ", resL1L2)


main()