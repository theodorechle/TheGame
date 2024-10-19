from generation.map_generation import MapGenerator
from chunk_manager import ChunkManager
from save_manager import SaveManager
from entities.player import Player
from map_chunk import Chunk
from items import Item
from logs import write_log
from typing import Any
from multiprocessing import Queue
import asyncio
import traceback
from random import randint

class Game:
    def __init__(self, seed: str|None, name: str, actions_queue: Queue, updates_queue: Queue) -> None:
        super().__init__()
        self.actions_queue: Queue = actions_queue
        self.updates_queue: Queue = updates_queue
        self.save_manager = SaveManager(name)
        infos = self.save_manager.load_generation_infos()
        if infos is None:
            if seed is None:
                seed = str(randint(-500000000, 500000000))
            self.save_manager.save_generation_infos({'seed': seed})
        else:
            seed = infos['seed']
        map_generator = MapGenerator(seed)
        self.chunk_manager = ChunkManager(map_generator, self.save_manager)
        self.players: dict[str, Player] = {}
        self.updated_blocks: dict[tuple[int, int], Item] = {}
        self.new_players: list[str] = []
        self.removed_players: list[str] = []
        self.UPDATE_DELAY_MS = 50
    
    def get_name(self) -> str:
        return self.save_manager.save_name

    def get_nb_players(self) -> int:
        return len(self.players)

    def create_player(self, name: str, images_name: str) -> None:
        if name in self.players: return
        # add try to load player from save
        self.players[name] = Player(name, 0, Chunk.HEIGHT, 0, 0, False, self.chunk_manager, images_name=images_name)
        self.new_players.append(name)

        # for test purpose only
        self.players[name].hot_bar_inventory.add_element_at_pos(14, 20, 0)
        self.players[name].hot_bar_inventory.add_element_at_pos(15, 20, 1)

    def remove_player(self, name: str) -> None:
        if name in self.players:
            self.players.pop(name)
            self.removed_players.append(name)
            self.chunk_manager.remove_player(name)

    def get_player_infos(self, name: str)  -> Player|None:
        if name not in self.players: return
        return self.players[name][0].get_infos()
    
    async def run(self) -> None:
        try:
            await asyncio.gather(self.process_actions(), self.update())
        except BaseException as e:
            write_log(f'Error in game {self.save_manager.save_name}: {repr(e)}', is_err=True)
            write_log(f'Detail: {traceback.format_exc()}', is_err=True)
    
    async def process_actions(self) -> None:
        while True:
            actions = await asyncio.get_running_loop().run_in_executor(None, self.actions_queue.get)
            self.player_updates(actions['name'], actions['actions'], actions['additional_data'])

    def player_updates(self, player_name: str, actions: list[str], additional_data: dict[str, Any]|None) -> dict[str, Any]:
        if additional_data is None: additional_data = {}
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
                    if 'interacted_block' not in additional_data or 'selected' not in additional_data: continue
                    block_pos = tuple(additional_data['interacted_block'])
                    block = player.place_block(block_pos, additional_data['selected'])
                    if block is not None: self.updated_blocks[block[1]] = block[0]
                case 'remove_block':
                    if 'interacted_block' not in additional_data: continue
                    block_pos = tuple(additional_data['interacted_block'])
                    block = player.remove_block(block_pos)
                    if block is not None: self.updated_blocks[block[1]] = block[0]
                case 'drag-item':
                    if 'item-pos' not in additional_data: continue
                    item_pos = tuple(additional_data['item-pos'])
                    
                case _:
                    write_log(f"Invalid player action '{action}'", True)

    async def update(self) -> None:
        while True:
            players_dict: dict[str, Any] = {}
            for player_name, player in self.players.items():
                has_changed = player.update(0) # temp value
                if player_name in self.new_players:
                    players_dict[player_name] = player.get_all_infos()
                elif has_changed:
                    players_dict[player_name] = player.get_infos()
                player.main_inventory.indexes_to_update.clear()
                player.hot_bar_inventory.indexes_to_update.clear()
            for player in self.removed_players:
                players_dict[player] = {'removed': True}
            self.removed_players.clear()
            if players_dict or self.updated_blocks:
                for player_name, player in self.players.items():
                    if player_name in self.new_players:
                        self.new_players.remove(player_name)
                        players = self.get_all_players_infos()
                    else:
                        players = players_dict
                    blocks_pos = []
                    blocks = []
                    for pos, block in self.updated_blocks.items():
                        blocks_pos.append(pos)
                        blocks.append(block)
                    self.updates_queue.put((player_name, {'players': players, 'blocks': [blocks_pos, blocks]}))
            self.updated_blocks.clear()
            await asyncio.sleep(0.05)

    def save(self) ->None:
        self.chunk_manager

    def get_all_players_infos(self) -> dict[str, Any]:
        return {player.name: player.get_all_infos() for player in self.players.values()}

    def get_infos(self) -> str:
        return {'seed': self.chunk_manager.map_generator.seed}
    