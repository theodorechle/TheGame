from map_generation import MapGenerator
from chunk_manager import ChunkManager
from save_manager import SaveManager
from player import Player
from map_chunk import Chunk

class Game:
    def __init__(self, seed, name) -> None:
        map_generator = MapGenerator(seed)
        map_generator.create_seeds()
        self.save_manager = SaveManager(name)
        self.chunk_manager = ChunkManager(map_generator, self.save_manager)
        self.players: dict[str, Player] = {}
    
    def create_player(self, name: str) -> None:
        if name in self.players: return
        # add try to load player from save
        self.players[name] = Player(name, 0, Chunk.HEIGHT, 0, 0, True)

    def get_player_infos(self, name: str) -> Player|None:
        if name not in self.players: return
        return self.players[name].get_infos()