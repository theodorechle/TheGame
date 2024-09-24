import generation.biomes as biomes
import blocks
import random
from map_chunk import Chunk
from generation.tree import Tree
from typing import Any
from generation.perlin import Perlin

class MapGenerator:
    def __init__(self, seed: str|None = None) -> None:
        self.seed = seed if seed is not None else str(random.randint(-500000000, 500000000))
        self.water_height: int = 40
        self.chunk_height_generator: Perlin = Perlin(self.seed, 6, 2, 2, 3, 0.5, 2)
        self.height_generator: Perlin = Perlin(self.seed, Chunk.HEIGHT * 2, 2, 2, 3, 0.5, 2)
        self.humidity_generator: Perlin = Perlin(self.seed, 20, 2, 2, 3, 0.5, 2)
        self.temperature_generator: Perlin = Perlin(self.seed, 20, 2, 2, 3, 0.5, 2)
        self.cave_radius_generator: Perlin = Perlin(self.seed, 20, 2, 2, 3, 0.5, 2)
        self.cave_height_generator: Perlin = Perlin(self.seed, 50, 2, 2, 3, 0.5, 2)
        self.tree_generator: Perlin = Perlin(self.seed, 20, 2, 2, 3, 0.5, 2)

    def get_infos_to_save(self) -> dict[str, Any]:
        return {
            'seed': self.seed
        }

    def set_infos(self, infos: dict[str, Any]):
        self.seed = infos['seed']

    @staticmethod
    def generate_number(previous_value: int, max_gap: int, min_value: int, max_value: int, keep_same: float = 0.5) -> int:
        if random.random() < keep_same: return previous_value
        return min(max_value, max(min_value, previous_value + random.randint(-max_gap, max_gap)))

    def create_new_biome_values(self) -> tuple[int, int]:
        return (1, 1)
    
    def generate_land_shape(self, chunk: Chunk) -> None:
        previous_biome_distance = 0
        chunk.blocks = [blocks.AIR for _ in range(Chunk.HEIGHT * Chunk.LENGTH)]
        used_biome = None
        last_biome = biomes.BIOMES[(max(round(self.chunk_height_generator.generate(Chunk.LENGTH * chunk.id)), -1), 1, 1)]
        for x in range(Chunk.LENGTH):
            height = round(self.height_generator.generate(Chunk.LENGTH * chunk.id + x))
            used_x = x if chunk.direction else (Chunk.LENGTH - 1 - x)
            if last_biome is not None and (height > chunk.biome.max_height or height < chunk.biome.min_height):
                used_biome = last_biome
                previous_biome_distance = 0
            else:
                used_biome = chunk.biome
                previous_biome_distance += 1
            
            min_ = max(min(chunk.biome.min_height - height, 0), -used_biome.max_height_difference)
            max_ = min(max(chunk.biome.max_height - height, 0), used_biome.max_height_difference)
            height = height + random.randint(min_, max_)
            height = min(Chunk.HEIGHT - 1, height)
            for y in range(height):
                chunk.blocks[y * Chunk.LENGTH + used_x] = blocks.STONE
            for y in range(height, self.water_height):
                chunk.blocks[y * Chunk.LENGTH + used_x] = blocks.WATER
            if 0 < previous_biome_distance < 3 and last_biome is not None:
                used_biome = last_biome
                biome2 = chunk.biome
            else:
                biome2 = None
            self.place_biome_blocks(chunk.blocks, used_biome, used_x, height, biome2)

    def place_biome_blocks(self, blocks_chunk: list[list[blocks.Block]], biome: biomes.Biome, x: int, last_height_before: int, biome2: biomes.Biome|None = None) -> None:
        last_add_y = 0
        last_height = last_height_before
        for zone in biome.blocks_by_zone:
            add_y = random.randint(0, 5)
            min_height = max(zone[1] + add_y, last_height - zone[2])
            for y in range(min_height, last_height + last_add_y):
                if blocks_chunk[y * Chunk.LENGTH + x] == blocks.STONE:
                    blocks_chunk[y * Chunk.LENGTH + x] = zone[0]
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
                    if blocks_chunk[y * Chunk.LENGTH + x] not in blocks.TRAVERSABLE_BLOCKS and (y == 0 or blocks_chunk[(y-1) * Chunk.LENGTH + x] not in blocks.TRAVERSABLE_BLOCKS) and random.random() > 0.4:
                        blocks_chunk[y * Chunk.LENGTH + x] = zone[0]
                last_add_y = add_y
                last_height = min_height
        if last_height_before < self.water_height:
            blocks_chunk[last_height_before * Chunk.LENGTH + x] = blocks.SAND

    @staticmethod
    def get_positions_for_ore_veins(chunk: Chunk, x: int, y: int, block: blocks.Block) -> list[tuple[int, int]]:
        pos: list[tuple[int, int]] = []
        if x > 0 and chunk.blocks[y * Chunk.LENGTH + x - 1] == block:
            pos.append((x - 1, y))
        if x < Chunk.LENGTH - 1 and chunk.blocks[y * Chunk.LENGTH + x + 1] == block:
            pos.append((x + 1, y))
        if y > 0 and chunk.blocks[(y - 1) * Chunk.LENGTH + x] == block:
            pos.append((x, y - 1))
        if y < Chunk.HEIGHT - 1 and chunk.blocks[(y + 1) * Chunk.LENGTH + x] == block:
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
            if chunk.blocks[vein_y * Chunk.LENGTH + vein_x] == blocks.STONE:
                pos.append((vein_x, vein_y))
            while pos:
                x, y = pos.pop(0)
                if random.random() < vein[4]:
                    chunk.blocks[y * Chunk.LENGTH + x] = vein[1]
                    pos += self.get_positions_for_ore_veins(chunk, x, y, blocks.STONE)

    def get_first_block_y(self, chunk: Chunk, x: int) -> int:
        y = Chunk.HEIGHT - 1
        while y > 0 and chunk.blocks[y * Chunk.LENGTH + x] in blocks.TRAVERSABLE_BLOCKS:
            y -= 1
        return y

    @staticmethod
    def can_place_leave(chunk: Chunk, x: int, y: int) -> bool:
        if chunk.biome.tree is None: return False
        if 0 > x or x >= Chunk.LENGTH - 1 or 0 > y or y >= Chunk.HEIGHT or chunk.blocks[y * Chunk.LENGTH + x] != chunk.biome.tree.grows_in: return False
        if x < Chunk.LENGTH - 1 and chunk.blocks[y * Chunk.LENGTH + x + 1] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leaves_block):
            return True
        if x > 0 and chunk.blocks[y * Chunk.LENGTH + x - 1] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leaves_block):
            return True
        if y < Chunk.HEIGHT - 1 and chunk.blocks[(y + 1) * Chunk.LENGTH + x] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leaves_block):
            return True
        if y > 0 and chunk.blocks[(y - 1) * Chunk.LENGTH + x] in (chunk.biome.tree.trunk_block, chunk.biome.tree.leaves_block):
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
                if chunk.blocks[y * Chunk.LENGTH + start_x] != blocks.GRASS: continue
                chunk.blocks[y * Chunk.LENGTH + start_x] = blocks.EARTH
                i = 0
                for i in range(1, random.randint(tree.min_trunk_height, tree.max_trunk_height)):
                    if y + i < Chunk.HEIGHT and chunk.blocks[(y + i) * Chunk.LENGTH + start_x] == tree.grows_in:
                        chunk.blocks[(y + i) * Chunk.LENGTH + start_x] = tree.trunk_block
                    else:
                        break
                if i < tree.min_trunk_height:
                    for j in range(i + 1):
                        chunk.blocks[(y + j) * Chunk.LENGTH + start_x] = tree.grows_in
                    continue
                start_y = y + i
                # leaves on the trunk
                center_min_y = random.randint(-tree.max_leaves_height, -tree.min_leaves_height)
                center_max_y = random.randint(tree.min_leaves_height, tree.max_leaves_height)
                for y in range(1, center_max_y + 1):
                    if self.can_place_leave(chunk, start_x, start_y + y):
                        chunk.blocks[(start_y + y) * Chunk.LENGTH + start_x] = tree.leaves_block
                # leaves before trunk
                min_y = center_min_y
                max_y = center_max_y
                nb_leaves_left = min(random.randint(-tree.max_leaves_width, -tree.min_leaves_width), min(start_x, Chunk.LENGTH - 1 - start_x))
                for x in range(-1, nb_leaves_left - 1, -1):
                    min_y, max_y = min(min_y + random.randint(0, 1), -tree.min_leaves_height), max(max_y - random.randint(0, 1), tree.min_leaves_height)
                    for y in range(min_y, max_y + 1):
                        if self.can_place_leave(chunk, start_x + x, start_y + y):
                            chunk.blocks[(start_y + y) * Chunk.LENGTH + start_x + x] = tree.leaves_block
                # leaves after trunk
                min_y = center_min_y
                max_y = center_max_y
                nb_leaves_right = min(max(nb_leaves_left + random.randint(-1, 1), tree.min_leaves_width), tree.max_leaves_width)
                for x in range(1, nb_leaves_right + 2):
                    min_y, max_y = min(min_y + random.randint(0, 1), -tree.min_leaves_height), max(max_y - random.randint(0, 1), tree.min_leaves_height)
                    for y in range(min_y, max_y + 1):
                        if self.can_place_leave(chunk, start_x + x, start_y + y):
                            chunk.blocks[(start_y + y) * Chunk.LENGTH + start_x + x] = tree.leaves_block

    @staticmethod
    def is_valid_pos(x: int, y: int, width: int, height: int) -> bool:
        return 0 <= x < width and 0 <= y < height

    def carve(self, chunk: Chunk, x: int, y: int, radius: int) -> None:
        if radius == 0 or y <= 0: return
        a = radius
        b = 0
        t1 = radius//16
        while a >= b:
            tmp_x = x + a
            for tmp_y in range(y - b, y + b):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] = blocks.AIR
            tmp_x = x + b
            for tmp_y in range(y - a, y + a):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] = blocks.AIR
            tmp_x = x - a
            for tmp_y in range(y - b, y + b):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] = blocks.AIR
            tmp_x = x - b
            for tmp_y in range(y - a, y + a):
                if self.is_valid_pos(tmp_x, tmp_y, Chunk.LENGTH, Chunk.HEIGHT) and chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] not in blocks.TRAVERSABLE_BLOCKS:
                    chunk.blocks[tmp_y * Chunk.LENGTH + tmp_x] = blocks.AIR
            b += 1
            t1 += b
            t2 = t1 - a
            if t2 >= 0:
                t1 = t2
                a -= 1


    def create_caves(self, chunk: Chunk) -> None:
        caves_pos_and_sizes: list[tuple[int, int]] = []
        max_cave_radius = 7
        for x in range(Chunk.LENGTH):
            radius = round(self.cave_radius_generator.generate(Chunk.LENGTH * x))
            start_y = round(self.cave_height_generator.generate(Chunk.LENGTH * x))
            while True:
                self.carve(chunk, x, start_y, radius)
                if (chunk.direction and x == Chunk.LENGTH - 1) or (not chunk.direction and x == 0):
                    caves_pos_and_sizes.append((start_y, radius))
                    break
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


    def generate_chunk(self, chunk_id: int) -> Chunk|None:
        # TODO: add use for temperature and humidity values
        # Don't use direction

        direction = chunk_id != 0

        height = max(round(self.chunk_height_generator.generate(Chunk.LENGTH * chunk_id)), -1)
        temperature = 1 # self.temperature_generator.generate(Chunk.LENGTH * chunk_id)
        humidity = 1 # self.humidity_generator.generate(Chunk.LENGTH * chunk_id)
        biome = biomes.BIOMES[(height, temperature, humidity)]

        chunk = Chunk(chunk_id, direction, biome)
        self.generate_land_shape(chunk)
        self.create_caves(chunk)
        self.place_ore_veins(chunk)
        return chunk