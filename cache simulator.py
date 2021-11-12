class Solution:
    def __init__(self):
        self.num_instruction_references = 0
        self.num_data_references = 0
        self.num_instruction_misses = 0
        self.num_data_misses = 0
        self.num_instruction_replaces = 0
        self.num_data_replaces = 0
        self.demand_fetch = 0
        self.copies_back = 0
        self.instruction_miss_rate = 0
        self.instruction_hit_rate = 0
        self.data_miss_rate = 0
        self.data_hit_rate = 0
        self.num_dirty_block = 0
        self.counter = 0


    def print_solution(self, type_cache, block_size, cache_size, associativity, write_policy, write_miss_policy):
        print('***CACHE SETTINGS***')
        if type_cache == 0:
            print('Unified I- D-cache')
            print('Size: {0}'.format(int(cache_size[0])))
        else:
            print('Split I- D-cache')
            print('I-cache size: {0}'.format(int(cache_size[0])))
            print('D-cache size: {0}'.format(int(cache_size[1])))
        print('Associativity: {0}'.format(associativity))
        print('Block size: {0}'.format(block_size))

        self.calculate_miss_rate_and_hit_rate()

        if write_policy == 'wb':
            print('Write policy: WRITE BACK')
        else:
            print('Write policy: WRITE THROUGH')
        if write_miss_policy == 'wa':
            print('Allocation policy: WRITE ALLOCATE')
        else:
            print('Allocation policy: WRITE NO ALLOCATE')
        print()
        print('***CACHE STATISTICS***')
        print('INSTRUCTIONS')
        print('accesses:', self.num_instruction_references)
        print('misses:', self.num_instruction_misses)
        print('miss rate: {0:.4f} (hit rate {1:.4f})'.format(self.instruction_miss_rate, self.instruction_hit_rate))
        print('replace:', self.num_instruction_replaces)
        print('DATA')
        print('accesses:', self.num_data_references)
        print('misses:', self.num_data_misses)
        print('miss rate: {0:.4f} (hit rate {1:.4f})'.format(self.data_miss_rate, self.data_hit_rate))
        print('replace:', self.num_data_replaces)
        print('TRAFFIC (in words)')
        print('demand fetch:', self.demand_fetch)
        print('copies back:', self.copies_back)

    def calculate_miss_rate_and_hit_rate(self):
        if self.num_instruction_references == 0 or self.num_instruction_misses == 0:
            self.instruction_miss_rate = round(0, 4)
            self.instruction_hit_rate = round(0, 4)

        if self.num_data_references == 0 or self.num_data_misses == 0:
            self.data_miss_rate = round(0, 4)
            self.data_hit_rate = round(0, 4)

        if self.num_instruction_references != 0 and self.num_instruction_misses != 0:
            self.instruction_miss_rate = round(self.num_instruction_misses / self.num_instruction_references, 4)
            self.instruction_hit_rate = 1 - self.instruction_miss_rate

        if self.num_data_references != 0 and self.num_data_misses != 0:
            self.data_miss_rate = round(self.num_data_misses / self.num_data_references, 4)
            self.data_hit_rate = 1 - self.data_miss_rate


s = Solution()


class Cache:
    def __init__(self, name, block_size, cache_size, associativity, write_policy, write_miss_policy):
        self.name = name
        self.block_size = block_size
        self.cache_size = cache_size
        self.block_count = int(cache_size / block_size)
        self.associativity = associativity
        self.write_policy = write_policy
        self.write_miss_policy = write_miss_policy
        self.blocks = [[Block(0, 0, 0, 0, 0) for i in range(associativity)] for j in
                       range(int(self.block_count / associativity))]

    def read_miss(self, block):
        dropped_block = self.blocks[int(block.index)].pop()
        self.blocks[int(block.index)].insert(0, block)
        s.demand_fetch += int(block_size / 4)
        if self.name == 'instruction_cache' or miss_type == 2:
            s.num_instruction_misses += 1
            if dropped_block.valid == 1:
                s.num_instruction_replaces += 1
        else:
            s.num_data_misses += 1
            if dropped_block.valid == 1:
                s.num_data_replaces += 1

        if dropped_block.dirty == 1:
            s.copies_back += int(self.block_size / 4)
            # s.num_dirty_block -= 1


    def read_hit(self, block):
        for i, item in enumerate(self.blocks[int(block.index)]):
            if item.check == block.check:
                d = self.blocks[int(block.index)].pop(i)
                if d.dirty == 1:
                    block.dirty = 1
                break
        self.blocks[int(block.index)].insert(0, block)

    def hit_or_miss_block(self, block):

        tag_existence = False
        for item in self.blocks[int(block.index)]:
            if item.check == block.check:
                if item.valid == 1:
                    tag_existence = True
                    break

        if tag_existence:

            if miss_type == 1:
                if self.write_policy == 'wb':
                    self.write_back_hit(block)
                else:
                    self.write_through_hit(block)
            else:
                self.read_hit(block)
            return 'hit'
        else:
            if miss_type == 1:
                if self.write_policy == 'wb':
                    self.write_back_miss(block)
                else:
                    self.write_through_miss(block)
            else:
                self.read_miss(block)
            return 'miss'

    def write_through_miss(self, block):
        allocate = self.write_miss_policy
        if allocate == 'wa':
            dropped_block = self.blocks[int(block.index)].pop()
            self.blocks[int(block.index)].insert(0, block)
            s.num_data_misses += 1
            s.demand_fetch += int(self.block_size / 4)

            if dropped_block.valid == 1:
                s.num_data_replaces += 1


        s.copies_back += 1

    def write_through_hit(self, block):
        # allocate = self.write_miss_policy
        # if allocate == 'wa':
        #     for i, item in enumerate(self.blocks[int(block.index)]):
        #         if item.check == block.check:
        #             self.blocks[int(block.index)].pop(i)
        #             self.blocks[int(block.index)].insert(0, block)
        #             break


        s.copies_back += 1

    def write_back_hit(self, block):
        for i, item in enumerate(self.blocks[int(block.index)]):
            if item.check == block.check:
                if item.dirty == 0:
                    s.num_dirty_block += 1

                item.dirty = 1
                # self.blocks[int(block.index)].pop(i)
                # self.blocks[int(block.index)].insert(0, block)
                break


    def write_back_miss(self, block):
        allocate = self.write_miss_policy
        if allocate == 'wa':
            dropped_block = self.blocks[int(block.index)].pop()
            if dropped_block.dirty == 1:
                s.copies_back += int(self.block_size / 4)
                s.num_dirty_block -= 1


            block.dirty = 1
            s.num_dirty_block += 1
            self.blocks[int(block.index)].insert(0, block)
            s.num_data_misses += 1
            s.demand_fetch += int(self.block_size / 4)

            if dropped_block.valid == 1:
                s.num_data_replaces += 1

        if allocate == 'nw':
            s.num_data_misses += 1
            s.copies_back += 1


class Block:
    def __init__(self, offset, tag, index, valid, dirty):
        self.offset = offset
        self.tag = tag
        self.index = index
        self.valid = valid
        self.dirty = dirty
        self.check = str(tag) + str(index)

    @classmethod
    def fill_block(cls, cache, address):
        offset = address % cache.block_size
        index = int(address / cache.block_size) % (int(cache.block_count / cache.associativity))
        tag = int(int(address / cache.block_size) / (int(cache.block_count / cache.associativity)))
        valid = 1
        dirty = 0
        return cls(offset, tag, index, valid, dirty)


# input
info = input().split(' - ')
block_size = int(info[0])
cache_architecture = int(info[1])
associativity = int(info[2])
write_policy = info[3]
write_miss_policy = info[4]
cache_size = input().split(' - ')
if cache_architecture == 0:
    cache = Cache('cache', block_size, int(cache_size[0]), associativity, write_policy, write_miss_policy)
else:
    instruction_cache = Cache('instruction_cache', block_size, int(cache_size[0]), associativity, write_policy,
                              write_miss_policy)
    data_cache = Cache('data_cache', block_size, int(cache_size[1]), associativity, write_policy, write_miss_policy)

# input (reference of memory)
while True:
    line = input()
    if line == '':
        break
    miss_type = int(line.split(' ')[0])

    if miss_type == 0 or miss_type == 1:
        s.num_data_references += 1
    elif miss_type == 2:
        s.num_instruction_references += 1

    memory_address = int(line.split(' ')[1], 16)


    if cache_architecture == 0:
        b = Block.fill_block(cache, memory_address)
        cache_name = cache
    else:
        if miss_type == 2:
            b = Block.fill_block(instruction_cache, memory_address)
            cache_name = instruction_cache
        else:
            b = Block.fill_block(data_cache, memory_address)
            cache_name = data_cache

    # check hit or miss and add index to block
    hit_or_miss = cache_name.hit_or_miss_block(b)
    # print(hit_or_miss)


try:
    for i in instruction_cache.blocks:
        for j in i:
            if j.dirty == 1:
                s.counter += 1
    for i in data_cache.blocks:
        for j in i:
            if j.dirty == 1:
                s.counter += 1
except NameError:
    for i in cache.blocks:
        for j in i:
            if j.dirty == 1:
                s.counter += 1


s.copies_back += (s.counter * int(block_size / 4))

s.print_solution(cache_architecture, block_size, cache_size, associativity, write_policy, write_miss_policy)
