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
        self.OCEAN_HEIGHT: int = 20
        self.height_generator: Perlin = Perlin(self.seed, 0.005, Chunk.HEIGHT, 3, 0.5, 1.5)
        # self.humidity_generator: Perlin = Perlin(self.seed, 2, Chunk.HEIGHT, 3, 0.5, 2)
        # self.temperature_generator: Perlin = Perlin(self.seed, 2, Chunk.HEIGHT, 3, 0.5, 2)
        # self.cave_radius_generator: Perlin = Perlin(self.seed, 2, Chunk.HEIGHT, 3, 0.5, 2)
        # self.cave_height_generator: Perlin = Perlin(self.seed, 2, Chunk.HEIGHT, 3, 0.5, 2)
        # self.tree_generator: Perlin = Perlin(self.seed, 2, Chunk.HEIGHT, 3, 0.5, 2)

    def get_infos_to_save(self) -> dict[str, Any]:
        return {
            'seed': self.seed
        }

    def set_infos(self, infos: dict[str, Any]):
        self.seed = infos['seed']

    @staticmethod
    def replace_blocks_vertically(chunk: Chunk, x: int, min_height: int, max_height: int, new_block: blocks.Block):
        for y in range(min_height, max_height):
            chunk.blocks[y * Chunk.LENGTH + x] = new_block

    @staticmethod
    def replace_specific_block_vertically(chunk: Chunk, x: int, min_height: int, max_height: int, block_to_replace: blocks.Block, new_block: blocks.Block):
        for y in range(min_height, max_height):
            index = y * Chunk.LENGTH + x
            if chunk.blocks[index] == block_to_replace:
                chunk.blocks[index] = new_block

    def generate_land_shape(self, chunk: Chunk) -> int:
        """
        Generate stone blocks to give the global form of the chunk
        return the chunk height (category (mountain, hill, plain, ...))
        """
        heights_sum: int = 0
        chunk.blocks = [blocks.AIR for _ in range(Chunk.HEIGHT * Chunk.LENGTH)]
        for x in range(Chunk.LENGTH):
            y: int = int(max(min(self.height_generator.generate(x + chunk.id*Chunk.LENGTH) + Chunk.HEIGHT // 2, Chunk.HEIGHT), 1))
            self.replace_blocks_vertically(chunk, x, 0, y, blocks.STONE)
            heights_sum += y
        return (heights_sum / Chunk.LENGTH) * biomes.MAX_HEIGHT // 100

    def add_oceans(self, chunk: Chunk) -> None:
        for x in range(Chunk.LENGTH):
            self.replace_specific_block_vertically(chunk, x, 0, self.OCEAN_HEIGHT, blocks.AIR, blocks.WATER)

    @staticmethod
    def get_top_height(chunk: Chunk, x: int) -> int:
        y = (Chunk.HEIGHT - 1) * Chunk.LENGTH
        while y > 0 and chunk.blocks[y + x] == blocks.AIR:
            y -= Chunk.LENGTH
        return y // Chunk.LENGTH

    def add_biome_blocks(self, chunk: Chunk, height: int, temperature: int, humidity: int) -> None:
        biome = biomes.BIOMES.get((height, temperature, humidity))
        if biome is None: return
        chunk.biome = biome

        for x in range(Chunk.LENGTH):
            last_height: int = self.get_top_height(chunk, x) + 1
            for zone in biome.blocks_by_zone:
                if last_height < zone[1]: continue
                add_y = random.randint(0, 3)
                min_height: int = min(max(zone[1] + add_y, last_height - zone[2]), Chunk.HEIGHT)
                self.replace_specific_block_vertically(chunk, x, min_height, last_height, blocks.STONE, zone[0])
                last_height = min_height + add_y

    @staticmethod
    def get_positions_for_ore_veins(chunk: Chunk, index: int, block: blocks.Block) -> list[tuple[int, int]]:
        pos: list[int] = []
        if index // Chunk.LENGTH != 0 and chunk.blocks[index - 1] == block:
            pos.append(index - 1)
        if index // Chunk.LENGTH != Chunk.LENGTH - 1 and chunk.blocks[index + 1] == block:
            pos.append(index)
        if index > Chunk.LENGTH and chunk.blocks[index - Chunk.LENGTH] == block:
            pos.append(index - Chunk.LENGTH)
        if index < (Chunk.HEIGHT - 1)*Chunk.LENGTH and chunk.blocks[index + Chunk.LENGTH] == block:
            pos.append(index + Chunk.LENGTH)
        return pos

    def add_ore_veins(self, chunk: Chunk) -> None:
        nb_ore_veins = random.randint(*chunk.biome.ore_veins_qty)
        ore_veins_probabilities = [vein[0] for vein in chunk.biome.ore_veins_repartition]
        for _ in range(nb_ore_veins):
            vein = random.choices(chunk.biome.ore_veins_repartition, weights=ore_veins_probabilities)[0]
            vein_index = random.randrange(vein[2], vein[3] + Chunk.LENGTH)
            pos: list[int] = []
            if chunk.blocks[vein_index] == blocks.STONE:
                pos.append(vein_index)
            while pos:
                index = pos.pop(0)
                if random.random() < vein[4]:
                    chunk.blocks[index] = vein[1]
                    pos.extend(self.get_positions_for_ore_veins(chunk, index, blocks.STONE))

    @staticmethod
    def can_place_leave(chunk: Chunk, index: int) -> bool:
        if chunk.biome.tree is None: return False
        # check if can place block
        if index < 0 or index >= Chunk.HEIGHT * Chunk.LENGTH or chunk.blocks[index] != chunk.biome.tree.grows_in: return False
        # check if surrounded by a trunk or leaves
        allowed_blocks = (chunk.biome.tree.trunk_block, chunk.biome.tree.leaves_block)
        if index // Chunk.LENGTH != 0 and chunk.blocks[index - 1] in allowed_blocks:
            return True
        if index // Chunk.LENGTH != Chunk.LENGTH - 1 and chunk.blocks[index + 1] in allowed_blocks:
            return True
        if index > Chunk.LENGTH and chunk.blocks[index - Chunk.LENGTH] in allowed_blocks:
            return True
        if index < (Chunk.HEIGHT - 1)*Chunk.LENGTH and chunk.blocks[index + Chunk.LENGTH] in allowed_blocks:
            return True
        return False

    def place_leaves_vertically(self, start: int, end: int, chunk: Chunk, position: int, leaves_block: blocks.Block) -> None:
        for y in range(start, end):
            if self.can_place_leave(chunk, position + y*Chunk.LENGTH):
                chunk.blocks[position + y*Chunk.LENGTH] = leaves_block

    def place_leaves_horizontally_and_vertically(self, min_y: int, max_y, min_x: int, max_x: int, step: int, tree: Tree, chunk: Chunk, position: int) -> None:
        for x in range(min_x, max_x, step):
            min_y, max_y = min(min_y + random.randint(0, 1), -tree.min_leaves_height), max(max_y - random.randint(0, 1), tree.min_leaves_height)
            self.place_leaves_vertically(min_y, max_y + 1, chunk, position + x, tree.leaves_block)


    def create_trees(self, chunk: Chunk) -> None:
        tree: Tree|None = chunk.biome.tree
        if tree is None: return
        if chunk.is_forest:
            spawn_chance = 0.8
        else:
            spawn_chance = tree.tree_spawn_chance
        for start_x in range(tree.min_leaves_width + 1, Chunk.LENGTH - tree.min_leaves_width - 1):
            if random.random() <= spawn_chance:
                # chunk if can place tree
                index = self.get_top_height(chunk, start_x)*Chunk.LENGTH + start_x
                if chunk.blocks[index] != blocks.GRASS: continue
                chunk.blocks[index] = blocks.EARTH

                # place trunk
                top_trunk_height = min(index + random.randint(tree.min_trunk_height, tree.max_trunk_height)*Chunk.LENGTH, Chunk.HEIGHT*Chunk.LENGTH)
                index += Chunk.LENGTH
                while index < top_trunk_height and chunk.blocks[index] == tree.grows_in:
                    chunk.blocks[index] = tree.trunk_block
                    index += Chunk.LENGTH
                
                index -= Chunk.LENGTH

                # leaves on the trunk
                center_min_y = random.randint(-tree.max_leaves_height, -tree.min_leaves_height)
                center_max_y = random.randint(tree.min_leaves_height, tree.max_leaves_height)
                self.place_leaves_vertically(1, center_max_y + 1, chunk, index, tree.leaves_block)
                
                # leaves before trunk
                nb_leaves_left = -min(random.randint(tree.min_leaves_width, tree.max_leaves_width), min(start_x, Chunk.LENGTH - 1 - start_x))
                self.place_leaves_horizontally_and_vertically(center_min_y, center_max_y, -1, nb_leaves_left - 1, -1, tree, chunk, index)

                # leaves after trunk
                nb_leaves_right = min(max(nb_leaves_left + random.randint(-1, 1), tree.min_leaves_width), tree.max_leaves_width)
                self.place_leaves_horizontally_and_vertically(center_min_y, center_max_y, 1, nb_leaves_right + 2, 1, tree, chunk, index)

    def generate_chunk(self, chunk_id: int) -> Chunk:
        random_state = random.getstate()
        random.seed(chunk_id)

        chunk: Chunk = Chunk(chunk_id, biomes.HILL)
        chunk_height: int = self.generate_land_shape(chunk)
        chunk_temperature: int = 1
        chunk_humidity: int = 1

        self.add_oceans(chunk)
        self.add_biome_blocks(chunk, chunk_height, chunk_temperature, chunk_humidity)
        self.add_ore_veins(chunk)
        self.create_trees(chunk)

        random.setstate(random_state)

        return chunk


"""
Land shape (height) OK
Choose biome OK
Carve caves
Replace with biome blocks OK
Place alterations (waterfalls, volcanos, ...)
Place trees OK
Place structures
"""