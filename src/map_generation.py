from biomes import Biome
import blocks
import random

class MapGenerator:
    def __init__(self, seed: str = str(random.randint(-500000000, 500000000))) -> None:
        self.seed = seed
        # states for next left and right chunks to be generated
        self.rand_states: list[tuple] = []
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
        self.biome_height_values = [random.randint(0, 2)] * 2
        self.last_block_height_values = [None] * 2
        self.temperature_values = [random.randint(0, 2)] * 2
        self.humidity_values = [random.randint(0, 2)] * 2
        self.rand_states = [random.getstate()] * 2
        random.seed(random.randbytes(150))
        self.rand_states[1] = random.getstate()

    @staticmethod
    def generate_number(previous_value: int, max_gap: int, min_value: int, max_value: int, keep_same: int = 0.5):
        if random.random() < keep_same: return previous_value
        return min(max_value, max(min_value, previous_value + random.randint(-max_gap, max_gap)))

    def generate_land_shape(self, chunk_height: int, chunk_length: int, min_height: int, max_height: int, max_height_difference: int, direction: int, upper_block: blocks.Block) -> list[list[blocks.Block]]:
        last_height = self.last_block_height_values[direction]
        if last_height is None:
            last_height = min_height + (max_height - min_height) // 2
        chunk = [[blocks.AIR for _ in range(chunk_length)] for _ in range(chunk_height)]
        if direction:
            x_range = range(chunk_length)
        else:
            x_range = range(chunk_length - 1, -1, -1)
        is_first_column = True
        for x in x_range:
            min_ = max(min(min_height - last_height, 0), -max_height_difference)
            max_ = min(max(max_height - last_height, 0), max_height_difference)
            height = last_height + random.randint(min_, max_)
            height = min(chunk_height - 1, height)
            for y in range(height):
                chunk[y][x] = blocks.STONE
            for y in range(height, self.water_height):
                chunk[y][x] = blocks.WATER
            if height >= self.water_height:
                chunk[height][x] = upper_block
            last_height = height
            if is_first_column and self.is_central_chunk:
                is_first_column = False
                self.last_block_height_values[not direction] = height

        self.last_block_height_values[direction] = last_height
        return chunk

    def fill_with_block(self, chunk: list[list[blocks.Block]], height: int, block: blocks.Block) -> list[list[blocks.Block]]:
        for x in range(len(chunk[0])):
            for y in range(height - 1, -1, -1):
                if chunk[y][x] != blocks.AIR:
                    break
                chunk[y][x] = block
        return chunk

    def generate_chunk(self, direction: str, chunk_length: int, chunk_height: int, central_chunk: bool = False) -> list[list[blocks.Block]]:
        """
        direction: 0 -> left, 1 -> right
        """
        self.is_central_chunk = central_chunk
        chunk: list[list[blocks.Block]] = None
        # TODO: add use for temperature and humidity values

        random.setstate(self.rand_states[direction])
        is_island = random.choices((0, 1), (0.3, 0.7))[0]
        if is_island:
            height = self.generate_number(self.biome_height_values[direction], 1, 0, 2, keep_same=0.4)
            if height == 0: # plain
                chunk = self.generate_land_shape(chunk_height, chunk_length, 50, 60, 1, direction, blocks.GRASS)
            if height == 1: # hill
                chunk = self.generate_land_shape(chunk_height, chunk_length, 60, 80, 2, direction, blocks.GRASS)
            if height == 2: # mountain
                chunk = self.generate_land_shape(chunk_height, chunk_length, 100, 115, 3, direction, blocks.STONE)
        else:
            chunk = self.generate_land_shape(chunk_height, chunk_length, 30, 40, 1, direction, blocks.STONE)
            height = self.biome_height_values[direction]

        # updates states and values
        self.rand_states[direction] = random.getstate()
        self.biome_height_values[direction] = height
        if self.is_central_chunk:
            self.biome_height_values[not direction] = self.biome_height_values[direction]
        return chunk