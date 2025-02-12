class CacheBlock:
    def __init__(self, tag):
        self.tag = tag
        self.dirty = False


class WriteBackCache:
    def __init__(self, total_size, block_size, associativity):
        self.total_size = total_size
        self.block_size = block_size
        self.associativity = associativity

        self.num_sets = total_size // (block_size * associativity)

        # Initialize empty sets
        self.cache = [[] for _ in range(self.num_sets)]

        self.read_hits = 0
        self.read_misses = 0
        self.write_hits = 0
        self.write_misses = 0
        self.write_backs = 0

    def _translate_ad_to_set_tag(self, address):

        block_index = address // self.block_size
        # By using the combination of set_index and tag, we can make sure every block is represented differently
        set_index = block_index % self.num_sets
        tag = block_index // self.num_sets

        return set_index, tag

    def read(self, address):
        set_index, tag = self._translate_ad_to_set_tag(address)

        # Get the corresponding cache set
        cache_set = self.cache[set_index]

        # Find matching block
        for i, block in enumerate(cache_set):
            if block.tag == tag:
                # Based on LRU, move the latest visited block to front
                cache_set.insert(0, cache_set.pop(i))
                self.read_hits += 1
                return

        # Block not found in cache
        self.read_misses += 1
        new_block = CacheBlock(tag)

        # If set is full, discard block based on LRU
        if len(cache_set) >= self.associativity:
            evicted = cache_set.pop(-1)
            if evicted.dirty:
                self.write_backs += 1

        cache_set.insert(0, new_block)

    def write(self, address):
        set_index, tag = self._translate_ad_to_set_tag(address)
        cache_set = self.cache[set_index]

        # Find matching block
        for i, block in enumerate(cache_set):
            if block.tag == tag:
                # Write hit
                cache_set.insert(0, cache_set.pop(i))
                block.dirty = True
                self.write_hits += 1
                return

        # Write miss
        self.write_misses += 1
        new_block = CacheBlock(tag)
        new_block.dirty = True
        # If set is full, discard block based on LRU
        if len(cache_set) >= self.associativity:
            evicted = cache_set.pop(-1)
            if evicted.dirty:
                self.write_backs += 1
        cache_set.insert(0, new_block)