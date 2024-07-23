import biomes
import blocks
import random

class MapGenerator:
    def __init__(self, seed: str = str(random.randint(-500000000, 500000000))) -> None:
        self.seed = seed
        # states for next left and right chunks to be generated
        self.rand_states: list[tuple] = []
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
        self.last_block_height_values = [None] * 2
        self.temperature_values = [random.randint(0, 2)] * 2
        self.humidity_values = [random.randint(0, 2)] * 2
        self.rand_states = [random.getstate()] * 2
        random.seed(random.randbytes(1))
        self.rand_states[1] = random.getstate()

    @staticmethod
    def generate_number(previous_value: int, max_gap: int, min_value: int, max_value: int, keep_same: int = 0.5):
        if random.random() < keep_same: return previous_value
        return min(max_value, max(min_value, previous_value + random.randint(-max_gap, max_gap)))

    def generate_land_shape(self, chunk_height: int, chunk_length: int, direction: int, biome: biomes.Biome) -> list[list[blocks.Block]]:
        last_height = self.last_block_height_values[direction]
        if last_height is None:
            last_height = biome.min_height + (biome.max_height - biome.min_height) // 2
        chunk = [[blocks.AIR for _ in range(chunk_length)] for _ in range(chunk_height)]
        if direction:
            x_range = range(chunk_length)
        else:
            x_range = range(chunk_length - 1, -1, -1)
        is_first_column = True
        for x in x_range:
            if self.last_biomes[direction] is not None and (last_height > biome.max_height or last_height < biome.min_height):
                used_biome = self.last_biomes[direction]
            else:
                used_biome = biome
                self.last_biomes[direction] = biome
            min_ = max(min(biome.min_height - last_height, 0), -used_biome.max_height_difference)
            max_ = min(max(biome.max_height - last_height, 0), used_biome.max_height_difference)
            height = last_height + random.randint(min_, max_)
            height = min(chunk_height - 1, height)
            for y in range(height):
                chunk[y][x] = blocks.STONE
            for y in range(height, self.water_height):
                chunk[y][x] = blocks.WATER
            if height <= self.water_height and not used_biome.is_water_biome:
                vars = biomes.get_biome_environment_values(used_biome)
                if vars is not None:
                    used_biome = biomes.BIOMES[(0, 0, vars[2], vars[3])]
            else:
                chunk[height][x] = used_biome.upper_block
            self.place_biome_blocks(chunk, x, used_biome, height)
            last_height = height
            if is_first_column and self.is_central_chunk:
                is_first_column = False
                self.last_block_height_values[not direction] = height

        self.last_block_height_values[direction] = last_height
        return chunk

    def place_biome_blocks(self, chunk: list[list[blocks.Block]], x: int, biome: biomes.Biome, last_height: int) -> None:
        for zone in biome.blocks_by_zone:
            for y in range(zone[1], last_height):
                if chunk[y][x] == blocks.STONE:
                    chunk[y][x] = zone[0]
            last_height = zone[1]


    def generate_chunk(self, direction: str, chunk_length: int, chunk_height: int, central_chunk: bool = False) -> tuple[list[list[blocks.Block]], str]:
        """
        direction: 0 -> left, 1 -> right
        """
        self.is_central_chunk = central_chunk
        chunk: list[list[blocks.Block]] = None
        # TODO: add use for temperature and humidity values

        random.setstate(self.rand_states[direction])
        is_island = random.choices((0, 1), (0.3, 0.7))[0]
        temperature = 0
        humidity = 0

        if is_island:
            height = self.generate_number(self.biome_height_values[direction], 1, 0, 2, keep_same=0.4)
            biome = biomes.BIOMES[(is_island, height, temperature, humidity)]
            chunk = self.generate_land_shape(chunk_height, chunk_length, direction, biome)
        else:
            biome = biomes.BIOMES[(is_island, 0, temperature, humidity)]
            chunk = self.generate_land_shape(chunk_height, chunk_length, direction, biome)
            height = self.biome_height_values[direction]
        # updates states and values
        self.rand_states[direction] = random.getstate()
        self.biome_height_values[direction] = height
        if self.is_central_chunk:
            self.biome_height_values[not direction] = self.biome_height_values[direction]
        return chunk, self.last_biomes[direction].name