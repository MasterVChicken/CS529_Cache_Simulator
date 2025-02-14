class CacheBlock:
    def __init__(self, tag):
        self.tag = tag
        self.dirty = False

class VictimCache:
    def __init__(self, size):
        self.size = size  # Number of blocks in the victim cache
        self.cache = []   # Fully associative storage

    def lookup(self, tag):
        """Check if the tag exists in the victim cache."""
        for i, block in enumerate(self.cache):
            if block.tag == tag:
                # Move accessed block to front (LRU policy)
                self.cache.insert(0, self.cache.pop(i))
                return block
        return None  # Miss

    def insert(self, evicted_block):
        """Insert an evicted block from L2 into the victim cache."""
        if len(self.cache) >= self.size:
            self.cache.pop(-1)  # Evict oldest block (FIFO)
        self.cache.insert(0, evicted_block)  # Insert new block at the front

    def remove(self, tag):
        """Remove a block manually (e.g., when moving to L2)."""
        self.cache = [block for block in self.cache if block.tag != tag]


class WriteBackCache:
    def __init__(self, total_size, block_size, associativity, lower_level_cache=None, victim_cache=None):
        self.total_size = total_size
        self.block_size = block_size
        self.associativity = associativity
        self.lower_level_cache = lower_level_cache
        self.victim_cache = victim_cache  # Add victim cache support

        self.num_sets = total_size // (block_size * associativity)
        self.cache = [[] for _ in range(self.num_sets)]  # Initialize empty sets

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
                cache_set.insert(0, cache_set.pop(i))  # Move to front (LRU)
                self.read_hits += 1
                return

        # L2 Miss: Check Victim Cache before main memory
        if self.victim_cache:
            victim_block = self.victim_cache.lookup(tag)
            if victim_block:
                self.victim_cache.remove(tag)
                if len(cache_set) >= self.associativity:
                    evicted = cache_set.pop(-1)  # Remove LRU block
                    self.victim_cache.insert(evicted)  # Move evicted block to Victim Cache
                cache_set.insert(0, victim_block)  # Move block from victim to L2
                self.read_hits += 1
                return

        # Read from lower level (L3 or main memory)
        self.read_misses += 1
        if self.lower_level_cache:
            self.lower_level_cache.read(address)

        # Insert new block into L2
        new_block = CacheBlock(tag)
        if len(cache_set) >= self.associativity:
            evicted = cache_set.pop(-1)
            if self.victim_cache:
                self.victim_cache.insert(evicted)  # Store evicted block in victim cache
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
                cache_set.insert(0, cache_set.pop(i))  # Move to front
                block.dirty = True
                self.write_hits += 1
                return

        # L2 Miss: Check Victim Cache before main memory
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
