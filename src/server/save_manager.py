from map_chunk import Chunk
import json
import os
from generation.biomes import BIOMES
from entities.player_interface import PlayerInterface
from save_manager_interface import SaveManagerInterface
from typing import Any
from module_infos import MODULE_PATH

SAVES_PATH: str = os.path.join(MODULE_PATH, 'saves')
FIRST_VERSIONNED_VERSION = 0.3
CURRENT_VERSION = 0.6

class SaveManager(SaveManagerInterface):
    def __init__(self, save_name: str) -> None:
        self.save_name = save_name
        self.save_path = os.path.join(SAVES_PATH, self.save_name)
        self.init_repository()

    @staticmethod
    def save_already_exists(save_name) -> bool:
        return os.path.exists(os.path.join(SAVES_PATH, save_name))

    def init_repository(self) -> None:
        self.chunks_path = os.path.join(self.save_path, 'chunks')
        self.players_path = os.path.join(self.save_path, 'players')
        self.generation_infos_path = os.path.join(self.save_path, 'generation_infos.json')
        os.makedirs(self.chunks_path, exist_ok=True)
        os.makedirs(self.players_path, exist_ok=True)

    def load_chunk(self, id: int) -> Chunk|dict[int, int]:
        try:
            with open(os.path.join(self.chunks_path, str(id) + '.json')) as f:
                chunk_dict = json.load(f)
        except FileNotFoundError:
            return
        version = chunk_dict.get('version', 0)
        # handle different versions
        if version <= 0.3:
            chunk: Chunk = Chunk(id, BIOMES[tuple(chunk_dict['biome'])])
            chunk.is_forest = chunk_dict['is_forest']
            chunk.blocks = chunk_dict['blocks']
            return chunk
        else:
            return chunk_dict['diffs']

    def save_chunk(self, chunk: Chunk|None) -> None:
        if chunk is None: return
        diffs: dict[int, int] = chunk.get_diffs()
        if not diffs: return
        chunk_dict = {
            'diffs': diffs,
            'version': CURRENT_VERSION
        }
        with open(os.path.join(self.chunks_path, str(chunk.id) + '.json'), 'w') as f:
            json.dump(chunk_dict, f)
    
    def load_players(self) -> dict[str, dict[str, Any]]|None:
        return
        players: dict[str, dict[str, Any]] = {}
        for player_file in os.listdir(self.players_path):
            try:
                with open(os.path.join(self.players_path, player_file)) as f:
                    player_infos = json.load(f)
                version = player_infos.get('version', 0)
                # handle versions
                if version < FIRST_VERSIONNED_VERSION:
                    player_infos['hot_bar_inventory'] = player_infos['inventory'][:10]
                    player_infos['main_inventory'] = player_infos['inventory'][10:]
                    player_infos.pop('inventory')

                player_infos['hot_bar_inventory'] = player_infos['hot_bar_inventory']
                player_infos['main_inventory'] = player_infos['main_inventory']
                players[player_file.removesuffix('.json')] = player_infos
            except FileNotFoundError:
                pass
        return players
    
    def save_players(self, players: list[PlayerInterface]) -> None:
        return
        for player in players:
            player_dict = {
                'direction': player.direction,
                'x': player.x,
                'y': player.y,
                'speed_x': player.speed_x,
                'speed_y': player.speed_y,
                'hot_bar_inventory': player.hot_bar_inventory.cells,
                'main_inventory': player.main_inventory.cells,
                'version': CURRENT_VERSION
            }
            with open(os.path.join(self.players_path, player.name + '.json'), 'w') as f:
                json.dump(player_dict, f)

    def load_generation_infos(self) -> dict[str, Any]|None:
        try:
            with open(self.generation_infos_path) as f:
                infos = json.load(f)
        except FileNotFoundError:
            return
        version = infos.get('version', 0)
        return infos
    
    def save_generation_infos(self, infos: dict[str, Any]) -> None:
        infos['version'] = CURRENT_VERSION
        with open(self.generation_infos_path, 'w') as f:
            json.dump(infos, f)