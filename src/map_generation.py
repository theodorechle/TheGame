from biomes import Biome
import blocks
import random

class MapGenerator:
    def __init__(self, seed: str) -> None:
        self.seed = seed
        # states for next left and right chunks to be generated
        self.rand_states: list[tuple] = []
        self.height_values: list[int] = []
        self.temperature_values: list[int] = []
        self.humidity_values: list[int] = []
        self.biomes: list[Biome] = [
            Biome("mountain"),
            Biome("plain"),
            Biome("ocean")
        ]
        # self.load_biomes_data()
        self.get_structures()

    def load_biomes_data(self):
        for biome in self.biomes:
            biome.load()

    def get_structures(self):
        ...
    
    def create_seeds(self, height: int):
        random.seed(self.seed)
        self.height_values = [random.choices(range(1, 3))[0]] * 2
        self.temperature_values = [random.choices((0, 1, 2))[0]] * 2
        self.humidity_values = [random.choices((0, 1, 2))[0]] * 2
        self.rand_states = [random.getstate()] * 2

    @staticmethod
    def generate_number(previous_value: int, max_gap: int, min_value: int, max_value: int):
        return min(max_value, max(min_value, previous_value + random.randint(-max_gap, max_gap)))


    def generate_chunk(self, direction: str, chunk_length: int, chunk_height: int) -> list[list[blocks.Block]]:
        """
        direction: 0 -> left, 1 -> right
        """
        chunk: list[list[blocks.Block]] = None
        # TODO: add use for temperature and humidity values

        random.setstate(self.rand_states[direction])
        is_island = random.choices((0, 1), (0.4, 0.6))
        if is_island:
            block = blocks.STONE
        else:
            block = blocks.WATER
        height = self.generate_number(self.height_values[direction], 2, 1, 3)
        chunk = [[block for _ in range(chunk_length)] for _ in range(height * (chunk_height // 4), chunk_height)] \
                + [[blocks.AIR for _ in range(chunk_length)] for _ in range(height * (chunk_height // 4))]
        self.rand_states[direction] = random.getstate()
        self.height_values[direction] = height
        return chunk