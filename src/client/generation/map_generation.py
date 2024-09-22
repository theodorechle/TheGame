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
        self.height_generator: Perlin = Perlin(self.seed, 0.005, Chunk.HEIGHT * 2, 3, 0.5, 1.5)
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
            chunk.blocks[y * chunk.LENGTH + x] = new_block

    @staticmethod
    def replace_specific_block_vertically(chunk: Chunk, x: int, min_height: int, max_height: int, block_to_replace: blocks.Block, new_block: blocks.Block):
        for y in range(min_height, max_height):
            index = y * chunk.LENGTH + x
            if chunk.blocks[index] == block_to_replace:
                chunk.blocks[index] = new_block

    def generate_land_shape(self, chunk: Chunk) -> int:
        """
        Generate stone blocks to give the global form of the chunk
        return the chunk height (category (mountain, hill, plain, ...))
        """
        heights_sum: int = 0
        chunk.blocks = [blocks.AIR for _ in range(Chunk.HEIGHT * Chunk.LENGTH)]
        for x in range(chunk.LENGTH):
            y: int = int(max(min(abs(self.height_generator.generate(x + chunk.id*chunk.LENGTH)), chunk.HEIGHT), 1))
            self.replace_blocks_vertically(chunk, x, 0, y, blocks.STONE)
            heights_sum += y
        return (heights_sum / chunk.LENGTH) * biomes.MAX_HEIGHT // 100

    def add_oceans(self, chunk: Chunk) -> None:
        for x in range(chunk.LENGTH):
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

        for x in range(chunk.LENGTH):
            last_height: int = self.get_top_height(chunk, x) + 1
            for zone in biome.blocks_by_zone:
                if last_height < zone[1]: continue
                min_height: int = max(zone[1], last_height - zone[2])
                self.replace_specific_block_vertically(chunk, x, min_height, last_height, blocks.STONE, zone[0])
                last_height = min_height

    def generate_chunk(self, chunk_id: int) -> Chunk:
        chunk: Chunk = Chunk(chunk_id, biomes.HILL)
        chunk_height: int = self.generate_land_shape(chunk)
        chunk_temperature: int = 1
        chunk_humidity: int = 1
        self.add_oceans(chunk)
        self.add_biome_blocks(chunk, chunk_height, chunk_temperature, chunk_humidity)
        return chunk


"""
Choose biome
Land shape (height)
Carve caves
Replace with biome blocks
Place alterations (waterfalls, volcanos, ...)
Place trees
Place structures
"""