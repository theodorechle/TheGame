from map_generation import MapGenerator
from save_manager import SaveManager

class Game:
    def __init__(self, seed, name) -> None:
        self.map_generator = MapGenerator(seed)
        self.map_generator.create_seeds()
        self.save_manager = SaveManager(name)
    