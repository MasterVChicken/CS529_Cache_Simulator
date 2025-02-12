class CacheBlock:
    def __init__(self, tag):
        self.tag = tag
        self.valid = False

class WriteThourghCache:
    def __init__(self, total_size, block_size, associativity):
        self.total_size = total_size
        self.block_size = block_size
        self.associativity = associativity

        self.num_sets = total_size // (block_size * associativity)
        # cache
        self.cache = [[] for _ in range(self.num_set)]

        self.hits = 0
        self.miss = 0

    def _translate_ad_to_set_tag(self, address):
        block_index = address // self.block_size
        set_index = block_index % self.num_sets
        tag = block_index // self.num_sets

        return set_index, tag
    
    def read(self, address):
        set_index, tag = self._translate_ad_to_set_tag(address)
        cache_set = self.cache[set_index]

        for i, block in enumerate(cache_set):
            if block.tag == tag and block.valid:
                cache_set.insert(0, cache_set.pop(i))
                self.hits += 1
                return
        
        # not found in cache
        self.miss += 1
        new_block = CacheBlock(tag)
        new_block.valid = True

        # for i, block in enumerate(cache_set):
        #     if not block.valid:
        #         cache_set.pop(i)
        
        if len(cache_set) >= self.associativity:
            cache_set.pop(-1)
        
        cache_set.insert(0,new_block)

        return

    def write(self, address):
        set_index, tag = self._translate_ad_to_set_tag(address)
        cache_set = self.cache[set_index]

        self.miss += 1

        for i, block in enumerate(cache_set):
            if block.tag == tag and block.valid:
                cache_set.insert(0, cache_set.pop(i))
                return
        
        # load from memory
        new_block = CacheBlock(tag)
        new_block.valid = True
        if len(cache_set) >= self.associativity:
            cache_set.pop(-1)
        cache_set.insert(0, new_block)

        return






    