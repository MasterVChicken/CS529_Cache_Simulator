from write_through_cache import CacheBlock, WriteThourghCache
from Write_back_Cache import CacheBlock, WriteBackCache

def simulate_write_throught_caches(trace, associativities, hit_time=1, miss_penalty=100):
    print ("Simulate Write Throught Caches")
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
        
        instr_miss_rate = instr_cache.miss / (instr_cache.miss + instr_cache.hits)
        data_miss_rate = data_cache.miss / (data_cache.miss + data_cache.hits)
        amat_instr = hit_time + (instr_miss_rate * miss_penalty)
        amat_data = hit_time + (data_miss_rate * miss_penalty)

        print(f"Associativity {assoc}: Instruction AMAT = {amat_instr:.2f}, Data AMAT = {amat_data:.2f}")

def simulate_write_back_caches(trace, associativities, hit_time=1, miss_penalty=100):
    print ("Simulate Write Back Caches")
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
        
        instr_miss_rate = (instr_cache.read_misses+instr_cache.write_misses) / \
                            ((instr_cache.read_misses+instr_cache.write_misses) + \
                            (instr_cache.read_hits+instr_cache.write_hits))
        data_miss_rate = (data_cache.read_misses+data_cache.write_misses) / \
                            ((data_cache.read_misses+data_cache.write_misses) + \
                            (data_cache.read_hits+data_cache.write_hits))
        amat_instr = hit_time + (instr_miss_rate * miss_penalty)
        amat_data = hit_time + (data_miss_rate * miss_penalty)

        print(f"Associativity {assoc}: Instruction AMAT = {amat_instr:.2f}, Data AMAT = {amat_data:.2f}")


def main():
    f = open("./traces/cc.trace", 'r')
    trace = []
    for line in f:
        str = line.split(" ")
        trace.append((int(str[0]), int(str[1][:-1],16)))
    f.close()

    associativities = [1, 2, 4, 8, 16, 32]

    simulate_write_throught_caches(trace, associativities)
    simulate_write_back_caches(trace, associativities)

main()