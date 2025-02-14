class CacheBlock:
    def __init__(self, tag):
        self.tag = tag
        self.dirty = False

class VictimCache:
    def __init__(self, size):
        self.size = size
        self.cache = []
        self.hits = 0
        self.miss = 0

    def lookup(self, tag):
        for i, block in enumerate(self.cache):
            if block.tag == tag:
                self.cache.insert(0, self.cache.pop(i))
                self.hits += 1
                return block
        self.miss += 1
        return

    def insert(self, evicted_block):
        if len(self.cache) >= self.size:
            self.cache.pop(-1)
        self.cache.insert(0, evicted_block)

    def remove(self, tag):
        self.cache = [block for block in self.cache if block.tag != tag]


class WriteBackCache:
    def __init__(self, total_size, block_size, associativity, lower_level_cache=None, victim_cache=None):
        self.total_size = total_size
        self.block_size = block_size
        self.associativity = associativity
        self.lower_level_cache = lower_level_cache
        self.victim_cache = victim_cache

        self.num_sets = total_size // (block_size * associativity)
        self.cache = [[] for _ in range(self.num_sets)]

        self.read_hits = 0
        self.read_misses = 0
        self.write_hits = 0
        self.write_misses = 0

    def _translate_ad_to_set_tag(self, address):
        block_index = address // self.block_size
        set_index = block_index % self.num_sets
        tag = block_index // self.num_sets
        return set_index, tag

    def read(self, address):
        set_index, tag = self._translate_ad_to_set_tag(address)
        cache_set = self.cache[set_index]

        # Check L1/L2 cache first
        for i, block in enumerate(cache_set):
            if block.tag == tag:
                cache_set.insert(0, cache_set.pop(i))
                self.read_hits += 1
                return

        # L2 Miss: Check Victim Cache before main memory
        if self.victim_cache:
            victim_block = self.victim_cache.lookup(tag)
            if victim_block:
                self.victim_cache.remove(tag)
                if len(cache_set) >= self.associativity:
                    # Remove LRU block
                    evicted = cache_set.pop(-1)
                    # Move evicted block to Victim Cache
                    self.victim_cache.insert(evicted)
                cache_set.insert(0, victim_block) 
                self.read_hits += 1
                return

        # Read from lower level
        self.read_misses += 1
        if self.lower_level_cache:
            self.lower_level_cache.read(address)

        # Insert new block into L2
        new_block = CacheBlock(tag)
        if len(cache_set) >= self.associativity:
            evicted = cache_set.pop(-1)
            if self.victim_cache:
                self.victim_cache.insert(evicted)
            else:
                if self.lower_level_cache:
                    evicted_address = (evicted.tag * self.num_sets + set_index) * self.block_size
                    self.lower_level_cache.write(evicted_address)

        cache_set.insert(0, new_block)

    def write(self, address):
        set_index, tag = self._translate_ad_to_set_tag(address)
        cache_set = self.cache[set_index]

        for i, block in enumerate(cache_set):
            if block.tag == tag:
                cache_set.insert(0, cache_set.pop(i))
                block.dirty = True
                self.write_hits += 1
                return

        # L2 Miss: Check Victim Cache
        if self.victim_cache:
            victim_block = self.victim_cache.lookup(tag)
            if victim_block:
                self.victim_cache.remove(tag)
                if len(cache_set) >= self.associativity:
                    evicted = cache_set.pop(-1)
                    self.victim_cache.insert(evicted)
                victim_block.dirty = True
                cache_set.insert(0, victim_block)
                self.write_hits += 1
                return

        # Write miss, fetch from lower cache or main memory
        self.write_misses += 1
        if self.lower_level_cache:
            self.lower_level_cache.read(address)

        # Insert new block into L2
        new_block = CacheBlock(tag)
        new_block.dirty = True
        if len(cache_set) >= self.associativity:
            evicted = cache_set.pop(-1)
            if self.victim_cache:
                self.victim_cache.insert(evicted)
            else:
                if self.lower_level_cache:
                    evicted_address = (evicted.tag * self.num_sets + set_index) * self.block_size
                    self.lower_level_cache.write(evicted_address)

        cache_set.insert(0, new_block)
