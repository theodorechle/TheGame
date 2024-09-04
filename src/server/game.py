from map_generation import MapGenerator
from chunk_manager import ChunkManager
from save_manager import SaveManager
from player import Player
from map_chunk import Chunk
from typing import Any
from logs import write_log

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
        self.players[name] = Player(name, 0, Chunk.HEIGHT, 0, 0, True, self.chunk_manager)

    def get_player_infos(self, name: str) -> Player|None:
        if name not in self.players: return
        return self.players[name].get_infos()
    
    def update(self, player_name: str, actions: list[str], player_update_dict: dict[str, Any]) -> dict[str, Any]:
        player = self.players[player_name]
        for action in actions:
            match action:
                case 'mv_left':
                    player.speed_x += 1
                case 'mv_right':
                    player.speed_x -= 1
                case 'mv_up':
                    player.speed_y += 1
                case 'place_block':
                    continue
                    player.place_block()
                case 'remove_block':
                    continue
                    player.remove_block()
                case _:
                    write_log(f"Invalid player action '{action}'", True)
        player.update(0) # TODO: change value
        return {
            'x': player.x,
            'y': player.y
        }