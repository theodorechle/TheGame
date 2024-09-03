import biomes
import blocks
import random
from map_chunk import Chunk
from tree import Tree
from typing import Any

class MapGenerator:
    def __init__(self, seed: str|None = None) -> None:
        if seed is None:
            self.seed = str(random.randint(-500000000, 500000000))
        else:
            self.seed = seed
        self.water_height: int = 40
        self.are_last_biomes_forests: list[bool] = []
        self.last_biomes: list[biomes.Biome|None] = []
        self.biome_height_values: list[int] = []
        self.last_block_height_values: list[int|None] = []
        self.temperature_values: list[int] = []
        self.humidity_values: list[int] = []
        self.last_caves_pos_and_sizes: list[list[tuple[int, int]]] = []
        self.last_chunks: list[int] = [0, 0]

    def get_infos_to_save(self) -> dict[str, Any]:
        return {
            'seed': self.seed,
            'are_last_biomes_forests': self.are_last_biomes_forests,
            'last_biomes': [biomes.get_biome_environment_values(biome) if biome is not None else biome for biome in self.last_biomes],
            'biome_height_values': self.biome_height_values,
            'last_block_height_values': self.last_block_height_values,
            'temperature_values': self.temperature_values,
            'humidity_values': self.humidity_values,
            'last_caves_pos_and_sizes': self.last_caves_pos_and_sizes
        }

    def set_infos(self, infos: dict[str, Any]):
        self.seed = infos['seed']
        self.are_last_biomes_forests = infos['are_last_biomes_forests']
        self.last_biomes = [biomes.BIOMES[tuple(biome)] if biome is not None else biome for biome in infos['last_biomes']]
        self.biome_height_values = infos['biome_height_values']
        self.last_block_height_values = infos['last_block_height_values']
        self.temperature_values = infos['temperature_values']
        self.humidity_values = infos['humidity_values']
        self.last_caves_pos_and_sizes = [[tuple(cave) for cave in infos_caves] for infos_caves in infos['last_caves_pos_and_sizes']]
        

    def create_seeds(self) -> None:
        random.seed(self.seed)
        self.last_biomes = [None, None]
        self.biome_height_values = [random.randint(0, 2)] * 2
        self.are_last_biomes_forests = [bool(random.randint(0, 1))] * 2
        self.last_block_height_values = [None] * 2
        self.last_caves_pos_and_sizes = [[], []]
        self.temperature_values = [1, 1]
        self.humidity_values = [1, 1]

    @staticmethod
    def generate_number(previous_value: int, max_gap: int, min_value: int, max_value: int, keep_same: float = 0.5) -> int:
        if random.random() < keep_same: return previous_value
        return min(max_value, max(min_value, previous_value + random.randint(-max_gap, max_gap)))

    def create_new_biome_values(self) -> tuple[int, int]:
        return (1, 1)
    
    def generate_land_shape(self, chunk: Chunk) -> None:
        last_height = self.last_block_height_values[chunk.direction]
        previous_biome_distance = 0
        if last_height is None:
            last_height = chunk.biome.min_height + (chunk.biome.max_height - chunk.biome.min_height) // 2
        chunk.blocks = [[blocks.AIR for _ in range(Chunk.LENGTH)] for _ in range(Chunk.HEIGHT)]
        used_biome = None
        for x in range(Chunk.LENGTH):
            used_x = x if chunk.direction else (Chunk.LENGTH - 1 - x)
            last_biome = self.last_biomes[chunk.direction]
            if last_biome is not None and (last_height > chunk.biome.max_height or last_height < chunk.biome.min_height):
                used_biome = last_biome
                previous_biome_distance = 0
            else:
                used_biome = chunk.biome
                previous_biome_distance += 1
            
            min_ = max(min(chunk.biome.min_height - last_height, 0), -used_biome.max_height_difference)
            max_ = min(max(chunk.biome.max_height - last_height, 0), used_biome.max_height_difference)
            height = last_height + random.randint(min_, max_)
            height = min(Chunk.HEIGHT - 1, height)
            for y in range(height):
                chunk.blocks[y][used_x] = blocks.STONE
            for y in range(height, self.water_height):
                chunk.blocks[y][used_x] = blocks.WATER
            if 0 < previous_biome_distance < 3 and last_biome is not None:
                used_biome = last_biome
                biome2 = chunk.biome
            else:
                biome2 = None
            self.place_biome_blocks(chunk.blocks, used_biome, used_x, height, biome2)
            last_height = height
            if x == 0 and chunk.id == 0:
                self.last_block_height_values[not chunk.direction] = height
        self.last_biomes[chunk.direction] = used_biome
        if chunk.id == 0:
            self.last_biomes[not chunk.direction] = used_biome

        self.last_block_height_values[chunk.direction] = last_height

    def place_biome_blocks(self, blocks_chunk: list[list[blocks.Block]], biome: biomes.Biome, x: int, last_height_before: int, biome2: biomes.Biome|None = None) -> None:
        last_add_y = 0
        last_height = last_height_before
        for zone in biome.blocks_by_zone:
            add_y = random.randint(0, 5)
            min_height = max(zone[1] + add_y, last_height - zone[2])
            for y in range(min_height, last_height + last_add_y):
                if blocks_chunk[y][x] == blocks.STONE:
                    blocks_chunk[y][x] = zone[0]
            last_add_y = add_y
            last_height = min_height      

        last_add_y = 0
        last_height = last_height_before
        if biome2 is not None:
            for zone in biome2.blocks_by_zone + [(blocks.STONE, 0)]:
                add_y = random.randint(0, 5)
                min_height = zone[1] + add_y
                if len(zone) == 3:
                    min_height = max(min_height, last_height - zone[2])
                for y in range(min_height, last_height + last_add_y):
                    if blocks_chunk[y][x] not in blocks.TRAVERSABLE_BLOCKS and (y == 0 or blocks_chunk[y-1][x] not in blocks.TRAVERSABLE_BLOCKS) and random.random() > 0.4:
                        blocks_chunk[y][x] = zone[0]
                last_add_y = add_y
                last_height = min_height
        if last_height_before < self.water_height:
            blocks_chunk[last_height_before][x] = blocks.SAND

    @staticmethod
    def get_positions_for_ore_veins(chunk: Chunk, x: int, y: int, block: blocks.Block) -> list[tuple[int, int]]:
        pos: list[tuple[int, int]] = []
        if x > 0 and chunk.blocks[y][x - 1] == block:
            pos.append((x - 1, y))
        if x < Chunk.LENGTH - 1 and chunk.blocks[y][x + 1] == block:
            pos.append((x + 1, y))
        if y > 0 and chunk.blocks[y - 1][x] == block:
            pos.append((x, y - 1))
        if y < Chunk.HEIGHT - 1 and chunk.blocks[y + 1][x] == block:
            pos.append((x, y + 1))
        return pos

    def place_ore_veins(self, chunk: Chunk) -> None:
        nb_ore_veins = random.randint(*chunk.biome.ore_veins_qty)
        ore_veins_probabilities = [vein[0] for vein in chunk.biome.ore_veins_repartition]
        for _ in range(nb_ore_veins):
            vein = random.choices(chunk.biome.ore_veins_repartition, weights=ore_veins_probabilities)[0]
            vein_x = random.randrange(0, Chunk.LENGTH)
            vein_y = random.randrange(vein[2], vein[3])
            pos: list[tuple[int, int]] = []
            if chunk.blocks[vein_y][vein_x] == blocks.STONE:
                pos.append((vein_x, vein_y))
            while pos:
                x, y = pos.pop(0)
                if random.random() < vein[4]:
                    chunk.blocks[y][x] = vein[1]
                    pos += self.get_positions_for_ore_veins(chunk, x, y, blocks.STONE)

    def get_first_block_y(self, chunk: Chunk, x: int) -> int:
        y = Chunk.HEIGHT - 1
        while y > 0 and chunk.blocks[y][x] in blocks.TRAVERSABLE_BLOCKS:
            y -= 1
        return y

    @staticmethod
    def can_place_leave(chunk: Chunk, x: int, y: int) -> bool:
        if chunk.biome.tree is None: return False
        if 0 > x or x >= Chunk.LENGTH - 1 or 0 > y or y >= Chunk.HEIGHT or chunk.blocks[y][x] != chunk.biome.tree.grows_in: return False
        if x < Chunk.LENGTH - 1 and chunk.blocks[y][x + 1] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leave_block):
            return True
        if x > 0 and chunk.blocks[y][x - 1] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leave_block):
            return True
        if y < Chunk.HEIGHT - 1 and chunk.blocks[y + 1][x] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leave_block):
            return True
        if y > 0 and chunk.blocks[y - 1][x] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leave_block):
            return True
        return False

    def create_trees(self, chunk: Chunk) -> None:
        tree: Tree|None = chunk.biome.tree
        if tree is None: return
        if chunk.is_forest:
            spawn_chance = 0.8
        else:
            spawn_chance = tree.tree_spawn_chance
        for start_x in range(tree.min_leaves_width + 1, Chunk.LENGTH - tree.min_leaves_width - 1):
            if random.random() <= spawn_chance:
                y = self.get_first_block_y(chunk, start_x)
                if chunk.blocks[y][start_x] != blocks.GRASS: continue
                chunk.blocks[y][start_x] = blocks.EARTH
                i = 0
                for i in range(1, random.randint(tree.min_trunk_height, tree.max_trunk_height)):
                    if y + i < Chunk.HEIGHT and chunk.blocks[y + i][start_x] == tree.grows_in:
                        chunk.blocks[y + i][start_x] = tree.trunk_block
                    else:
                        break
                if i < tree.min_trunk_height:
                    for j in range(i + 1):
                        chunk.blocks[y + j][start_x] = tree.grows_in
                    continue
                start_y = y + i
                # leaves on the trunk
                center_min_y = random.randint(-tree.max_leaves_height, -tree.min_leaves_height)
                center_max_y = random.randint(tree.min_leaves_height, tree.max_leaves_height)
                for y in range(1, center_max_y + 1):
                    if self.can_place_leave(chunk, start_x, start_y + y):
                        chunk.blocks[start_y + y][start_x] = tree.leave_block
                # leaves before trunk
                min_y = center_min_y
                max_y = center_max_y
                nb_leaves_left = min(random.randint(-tree.max_leaves_width, -tree.min_leaves_width), min(start_x, Chunk.LENGTH - 1 - start_x))
                for x in range(-1, nb_leaves_left - 1, -1):
                    min_y, max_y = min(min_y + random.randint(0, 1), -tree.min_leaves_height), max(max_y - random.randint(0, 1), tree.min_leaves_height)
                    for y in range(min_y, max_y + 1):
                        if self.can_place_leave(chunk, start_x + x, start_y + y):
                            chunk.blocks[start_y + y][start_x + x] = tree.leave_block
                # leaves after trunk
                min_y = center_min_y
                max_y = center_max_y
                nb_leaves_right = min(max(nb_leaves_left + random.randint(-1, 1), tree.min_leaves_width), tree.max_leaves_width)
                for x in range(1, nb_leaves_right + 2):
                    min_y, max_y = min(min_y + random.randint(0, 1), -tree.min_leaves_height), max(max_y - random.randint(0, 1), tree.min_leaves_height)
                    for y in range(min_y, max_y + 1):
                        if self.can_place_leave(chunk, start_x + x, start_y + y):
                            chunk.blocks[start_y + y][start_x + x] = tree.leave_block

    @staticmethod
    def is_valid_pos(x: int, y: int, width: int, height: int) -> bool:
        return 0 <= x < width and 0 <= y < height

    def carve(self, chunk: Chunk, x: int, y: int, radius: int) -> None:
        if radius == 0: return
        a = radius
        b = 0
        t1 = radius//16
        while a >= b:
            tmp_x = x + a
            for tmp_y in range(y - b, y + b):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y][tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y][tmp_x] = blocks.AIR
            tmp_x = x + b
            for tmp_y in range(y - a, y + a):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y][tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y][tmp_x] = blocks.AIR
            tmp_x = x - a
            for tmp_y in range(y - b, y + b):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y][tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y][tmp_x] = blocks.AIR
            tmp_x = x - b
            for tmp_y in range(y - a, y + a):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y][tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y][tmp_x] = blocks.AIR
            b += 1
            t1 += b
            t2 = t1 - a
            if t2 >= 0:
                t1 = t2
                a -= 1


    def create_caves(self, chunk: Chunk) -> None:
        caves_pos_and_sizes: list[tuple[int, int]] = []
        max_cave_radius = 7
        for _ in range(random.randint(len(self.last_caves_pos_and_sizes[chunk.direction]), 2)):
            force_continue = False
            if self.last_caves_pos_and_sizes[chunk.direction]:
                start_y, radius = self.last_caves_pos_and_sizes[chunk.direction].pop(0)
                x = 0 if chunk.direction else Chunk.LENGTH - 1
                force_continue = True
            else:
                radius = random.randint(0, max_cave_radius)
                x = random.randrange(radius * chunk.direction, Chunk.LENGTH - radius * (not chunk.direction))
                y = self.get_first_block_y(chunk, x)
                start_y = random.randint(0, y - radius)
            while True:
                self.carve(chunk, x, start_y, radius)
                if (chunk.direction and x + radius >= Chunk.LENGTH - 1) or (not chunk.direction and x - radius <= 0):
                    force_continue = True
                if (chunk.direction and x == Chunk.LENGTH - 1) or (not chunk.direction and x == 0):
                    caves_pos_and_sizes.append((start_y, radius))
                    break
                if not force_continue and not random.randint(0, 15):
                    break
                force_continue = False
                x += 1 if chunk.direction else -1
                if start_y > 0 and random.randint(0, 1):
                    start_y -= 1
                elif start_y < self.get_first_block_y(chunk, x) and random.randint(0, 1):
                    start_y += 1

                radius += random.randint(-1, 1)
                if radius > max_cave_radius:
                    radius -= 1
                elif radius < 0:
                    radius += 1
        self.last_caves_pos_and_sizes[chunk.direction] = caves_pos_and_sizes


    def generate_chunk(self, chunk_id: int) -> Chunk|None:
        # TODO: add use for temperature and humidity values
        # Don't use direction
        rand_state = random.getstate()
        random.seed(f'{self.seed}{chunk_id}')

        if chunk_id == 0 or chunk_id == self.last_chunks[0] - 1:
            direction = False
        elif chunk_id == self.last_chunks[1] + 1:
            direction = True
        else:
            return None

        height = self.biome_height_values[direction]
        temperature = self.temperature_values[direction]
        humidity = self.humidity_values[direction]
        biome = biomes.BIOMES[(height, temperature, humidity)]

        chunk = Chunk(chunk_id, direction, biome)
        self.generate_land_shape(chunk)
        self.create_caves(chunk)
        self.place_ore_veins(chunk)
        if biome.tree is not None:
            chunk.is_forest = self.are_last_biomes_forests[direction]
            if chunk.is_forest:
                if random.random() > biome.tree.stay_forest_chance:
                    chunk.is_forest = False
            else:
                if random.random() <= biome.tree.forest_spawn_chance:
                    chunk.is_forest = True
            self.are_last_biomes_forests[direction] = chunk.is_forest
            self.create_trees(chunk)
        else:
            chunk.is_forest = False

        self.biome_height_values[direction] = self.generate_number(self.biome_height_values[direction], 1, -1, 3, keep_same=0.4)
        self.temperature_values[direction], self.humidity_values[direction] = self.create_new_biome_values()
        self.last_chunks[direction] = chunk_id
        # updates states and values
        random.setstate(rand_state)
        if chunk.id == 0:
            self.biome_height_values[not direction] = self.biome_height_values[direction]
            self.last_chunks[not direction] = self.last_chunks[direction]
        return chunk