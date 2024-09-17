from map_generation import MapGenerator
from chunk_manager import ChunkManager
from save_manager import SaveManager
from player import Player
from map_chunk import Chunk
from typing import Any
from logs import write_log
from multiprocessing import Queue
import asyncio

class Game:
    def __init__(self, seed, name, actions_queue: Queue, updates_queue: Queue) -> None:
        super().__init__()
        self.actions_queue: Queue = actions_queue
        self.updates_queue: Queue = updates_queue
        map_generator = MapGenerator(seed)
        map_generator.create_seeds()
        self.save_manager = SaveManager(name)
        self.chunk_manager = ChunkManager(map_generator, self.save_manager)
        self.players: dict[str, Player] = {}
        self.updated_blocks: dict[tuple[int, int], int] = {}
        self.new_players: list[str] = []
        self.UPDATE_DELAY_MS = 50
    
    def get_name(self) -> str:
        return self.save_manager.save_name

    def create_player(self, name: str, images_name: str) -> None:
        if name in self.players: return
        # add try to load player from save
        self.players[name] = Player(name, 0, Chunk.HEIGHT, 0, 0, True, self.chunk_manager, images_name=images_name)
        self.new_players.append(name)

    def get_player_infos(self, name: str) -> Player|None:
        if name not in self.players: return
        return self.players[name][0].get_infos()
    
    async def run(self) -> None:
        await asyncio.gather(self.process_actions(), self.update())
    
    async def process_actions(self) -> None:
        while True:
            actions = await asyncio.get_running_loop().run_in_executor(None, self.actions_queue.get)
            self.player_updates(actions['name'], actions['actions'])

    def player_updates(self, player_name: str, actions: list[str]) -> dict[str, Any]:
        player = self.players[player_name]
        for action in actions:
            match action:
                case 'mv_left':
                    player.speed_x = -1
                case 'mv_right':
                    player.speed_x = 1
                case 'mv_up':
                    player.speed_y = 1
                case 'place_block':
                    continue
                    player.place_block()
                case 'remove_block':
                    continue
                    player.remove_block()
                case _:
                    write_log(f"Invalid player action '{action}'", True)

    async def update(self) -> None:
        while True:
            players_dict: dict[str, Any] = {}
            for player_name, player in self.players.items():
                has_changed = player.update(0) # temp value
                if player_name in self.new_players:
                    players_dict[player_name] = player.get_all_infos()
                if has_changed:
                    players_dict[player_name] = player.get_infos()
            if players_dict:
                for player_name, player in self.players.items():
                    if player_name in self.new_players:
                        self.updates_queue.put((player_name, self.get_all_players_infos()))
                    self.updates_queue.put((player_name, {'players': players_dict}))
            await asyncio.sleep(0.05)

    def get_all_players_infos(self) -> dict[str, Any]:
        return {
            'players': {player.name: player.get_all_infos() for player in self.players.values()}
        }
