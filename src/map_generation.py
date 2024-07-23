import biomes
import blocks
import random

class MapGenerator:
    def __init__(self, seed: str = str(random.randint(-500000000, 500000000))) -> None:
        self.seed = seed
        # states for next left and right chunks to be generated
        self.rand_states: list[tuple] = []
        self.are_last_biomes_forests: list[bool] = []
        self.last_biomes: list[biomes.Biome|None] = []
        self.biome_height_values: list[int] = []
        self.last_block_height_values: list[int|None] = []
        self.temperature_values: list[int] = []
        self.humidity_values: list[int] = []
        self.is_central_chunk = False
        self.water_height: int = 50
        # self.load_biomes_data()
        self.get_structures()

    def load_biomes_data(self):
        for biome in self.biomes:
            biome.load()

    def get_structures(self):
        ...
    
    def create_seeds(self):
        random.seed(self.seed)
        self.last_biomes = [None] * 2
        self.biome_height_values = [random.randint(0, 2)] * 2
        self.are_last_biomes_forests = [bool(random.randint(0, 1))] * 2
        self.last_block_height_values = [None] * 2
        self.temperature_values = [1] * 2
        self.humidity_values = [1] * 2
        self.rand_states = [random.getstate()] * 2
        random.seed(random.randbytes(1))
        self.rand_states[1] = random.getstate()

    @staticmethod
    def generate_number(previous_value: int, max_gap: int, min_value: int, max_value: int, keep_same: int = 0.5):
        if random.random() < keep_same: return previous_value
        return min(max_value, max(min_value, previous_value + random.randint(-max_gap, max_gap)))

    def create_new_biome_values(self, direction: bool):
        return (1, 1)
    
    def generate_land_shape(self, chunk_height: int, chunk_length: int, direction: int, biome: biomes.Biome) -> list[list[blocks.Block]]:
        last_height = self.last_block_height_values[direction]
        previous_biome_distance = 0
        if last_height is None:
            last_height = biome.min_height + (biome.max_height - biome.min_height) // 2
        chunk = [[blocks.AIR for _ in range(chunk_length)] for _ in range(chunk_height)]
        for x in range(chunk_length):
            used_x = x if direction else (chunk_length - 1 - x)
            if self.last_biomes[direction] is not None and (last_height > biome.max_height or last_height < biome.min_height):
                used_biome = self.last_biomes[direction]
                previous_biome_distance = 0
            else:
                used_biome = biome
                previous_biome_distance += 1
            min_ = max(min(biome.min_height - last_height, 0), -used_biome.max_height_difference)
            max_ = min(max(biome.max_height - last_height, 0), used_biome.max_height_difference)
            height = last_height + random.randint(min_, max_)
            height = min(chunk_height - 1, height)
            for y in range(height):
                chunk[y][used_x] = blocks.STONE
            for y in range(height, self.water_height):
                chunk[y][used_x] = blocks.WATER
            if height >= self.water_height:
                chunk[height][used_x] = used_biome.upper_block
            else:
                chunk[height][used_x] = blocks.SAND
            if 0 < previous_biome_distance < 3 and self.last_biomes[direction] is not None:
                used_biome = self.last_biomes[direction]
                biome2 = biome
            else:
                biome2 = None
            self.place_biome_blocks(chunk, used_x, used_biome, height, biome2)
            last_height = height
            if x == 0 and self.is_central_chunk:
                self.last_block_height_values[not direction] = height
        self.last_biomes[direction] = used_biome
        if self.is_central_chunk:
            self.last_biomes[not direction] = used_biome

        self.last_block_height_values[direction] = last_height
        return chunk

    def place_biome_blocks(self, chunk: list[list[blocks.Block]], x: int, biome: biomes.Biome, last_height_before: int, biome2: biomes.Biome|None = None) -> None:
        last_add_y = 0
        last_height = last_height_before
        for zone in biome.blocks_by_zone:
            max_size = zone[2] if len(zone) == 3 else last_height
            add_y = random.randint(0, 5)
            for y in range(max(zone[1] + add_y, last_height - max_size), last_height + last_add_y):
                if chunk[y][x] == blocks.STONE:
                    chunk[y][x] = zone[0]
            last_add_y = add_y
            last_height = zone[1]        

        last_add_y = 0
        last_height = last_height_before
        if biome2 is not None:
            for zone in biome2.blocks_by_zone + [(blocks.STONE, 0)]:
                max_size = zone[2] if len(zone) == 3 else last_height
                add_y = random.randint(0, 5)
                for y in range(max(zone[1] + add_y, last_height - max_size), last_height + last_add_y):
                    if chunk[y][x] not in blocks.TRAVERSABLE_BLOCKS and (y == 0 or chunk[y-1][x] not in blocks.TRAVERSABLE_BLOCKS) and random.random() > 0.4:
                        chunk[y][x] = zone[0]
                last_add_y = add_y
                last_height = zone[1]

    @staticmethod
    def get_positions_for_ore_veins(chunk: list[list[blocks.Block]], x: int, y: int, block: blocks.Block) -> list[tuple[int, int]]:
        pos = []
        if x > 0 and chunk[y][x - 1] == block:
            pos.append((x - 1, y))
        if x < len(chunk[0]) - 1 and chunk[y][x + 1] == block:
            pos.append((x + 1, y))
        if y > 0 and chunk[y - 1][x] == block:
            pos.append((x, y - 1))
        if y < len(chunk) - 1 and chunk[y + 1][x] == block:
            pos.append((x, y + 1))
        return pos

    def place_ore_veins(self, chunk: list[list[blocks.Block]], biome: biomes.Biome):
        nb_ore_veins = random.randint(*biome.ore_veins_qty)
        ore_veins_probabilities = [vein[0] for vein in biome.ore_veins_repartition]
        for _ in range(nb_ore_veins):
            vein = random.choices(biome.ore_veins_repartition, weights=ore_veins_probabilities)[0]
            vein_x = random.randrange(0, len(chunk[0]))
            vein_y = random.randrange(vein[2], vein[3])
            pos = []
            if chunk[vein_y][vein_x] == blocks.STONE:
                pos.append((vein_x, vein_y))
            while pos:
                x, y = pos.pop(0)
                if random.random() < vein[4]:
                    chunk[y][x] = vein[1]
                    pos += self.get_positions_for_ore_veins(chunk, x, y, blocks.STONE)

    def get_first_block_y(self, chunk: list[list[blocks.Block]], x: int) -> int:
        y = len(chunk) - 1
        while y > 0 and chunk[y][x] in blocks.TRAVERSABLE_BLOCKS:
            y -= 1
        return y

    @staticmethod
    def can_place_leave(chunk: list[list[blocks.Block]], x: int, y: int, tree: biomes.Tree) -> bool:
        if 0 > x or x >= len(chunk[0]) - 1 or 0 > y or y >= len(chunk) or chunk[y][x] != tree.grows_in: return False
        if x < len(chunk[0]) - 1 and chunk[y][x + 1] in (tree.trunk_block, tree.leave_block):
            return True
        if x > 0 and chunk[y][x - 1] in (tree.trunk_block, tree.leave_block):
            return True
        if y < len(chunk) - 1 and chunk[y + 1][x] in (tree.trunk_block, tree.leave_block):
            return True
        if y > 0 and chunk[y - 1][x] in (tree.trunk_block, tree.leave_block):
            return True

    def create_trees(self, chunk: list[list[blocks.Block]], biome: biomes.Biome, is_forest: bool) -> None:
        tree = biome.tree
        if is_forest:
            spawn_chance = 0.8
        else:
            spawn_chance = tree.tree_spawn_chance
        for start_x in range(tree.min_leaves_width, len(chunk[0]) - tree.min_leaves_width):
            if random.random() <= spawn_chance:
                y = self.get_first_block_y(chunk, start_x)
                if chunk[y][start_x] != blocks.GRASS: continue
                chunk[y][start_x] = blocks.EARTH
                for i in range(1, random.randint(tree.min_trunk_height, tree.max_trunk_height)):
                    if y + i < len(chunk) and chunk[y + i][start_x] == tree.grows_in:
                        chunk[y + i][start_x] = tree.trunk_block
                    else:
                        break
                if i < tree.min_trunk_height:
                    for j in range(i + 1):
                        chunk[y + j][start_x] = tree.grows_in
                    continue
                start_y = y + i
                # leaves on the trunk
                center_min_y = random.randint(-tree.max_leaves_height, -tree.min_leaves_height)
                center_max_y = random.randint(tree.min_leaves_height, tree.max_leaves_height)
                for y in range(1, center_max_y + 1):
                    if self.can_place_leave(chunk, start_x, start_y + y, tree):
                        chunk[start_y + y][start_x] = tree.leave_block
                # leaves before trunk
                min_y = center_min_y
                max_y = center_max_y
                nb_leaves_left = random.randint(-tree.max_leaves_width, -tree.min_leaves_width)
                for x in range(-1, nb_leaves_left - 1, -1):
                    min_y, max_y = min(min_y + random.randint(0, 1), -tree.min_leaves_height), max(max_y - random.randint(0, 1), tree.min_leaves_height)
                    for y in range(min_y, max_y + 1):
                        if self.can_place_leave(chunk, start_x + x, start_y + y, tree):
                            chunk[start_y + y][start_x + x] = tree.leave_block
                # leaves after trunk
                min_y = center_min_y
                max_y = center_max_y
                nb_leaves_right = min(max(nb_leaves_left + random.randint(-1, 1), tree.min_leaves_width), tree.max_leaves_width)
                for x in range(1, nb_leaves_right + 2):
                    min_y, max_y = min(min_y + random.randint(0, 1), -tree.min_leaves_height), max(max_y - random.randint(0, 1), tree.min_leaves_height)
                    for y in range(min_y, max_y + 1):
                        if self.can_place_leave(chunk, start_x + x, start_y + y, tree):
                            chunk[start_y + y][start_x + x] = tree.leave_block

    def generate_chunk(self, direction: bool, chunk_length: int, chunk_height: int, central_chunk: bool = False) -> tuple[list[list[blocks.Block]], str]:
        """
        direction: 0 -> left, 1 -> right
        """
        self.is_central_chunk = central_chunk
        chunk: list[list[blocks.Block]] = None
        # TODO: add use for temperature and humidity values
        random.setstate(self.rand_states[direction])

        height = self.biome_height_values[direction]
        temperature = self.temperature_values[direction]
        humidity = self.humidity_values[direction]
        biome = biomes.BIOMES[(height, temperature, humidity)]
        chunk = self.generate_land_shape(chunk_height, chunk_length, direction, biome)
        if biome.tree is not None:
            is_forest = self.are_last_biomes_forests[direction]
            if is_forest:
                if random.random() > biome.tree.stay_forest_chance:
                    is_forest = False
            else:
                if random.random() <= biome.tree.forest_spawn_chance:
                    is_forest = True
            self.are_last_biomes_forests[direction] = is_forest
            self.create_trees(chunk, biome, is_forest)
        else:
            is_forest = False
        self.place_ore_veins(chunk, biome)

        self.biome_height_values[direction] = self.generate_number(self.biome_height_values[direction], 1, -1, 2, keep_same=0.4)
        self.temperature_values[direction], self.humidity_values[direction] = self.create_new_biome_values(direction)

        # updates states and values
        self.rand_states[direction] = random.getstate()
        if self.is_central_chunk:
            self.biome_height_values[not direction] = self.biome_height_values[direction]
        return chunk, self.last_biomes[direction].name, is_forest