from map_generation import MapGenerator
from chunk_manager import ChunkManager
from save_manager import SaveManager

class Game:
    def __init__(self, seed, name) -> None:
        map_generator = MapGenerator(seed)
        map_generator.create_seeds()
        self.save_manager = SaveManager(name)
        self.chunk_manager = ChunkManager(map_generator, self.save_manager)