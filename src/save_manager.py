from map_chunk import Chunk, blocks_to_int, int_to_blocks
import json
import os
from biomes import BIOMES, get_biome_environment_values
from player_interface import PlayerInterface
from save_manager_interface import SaveManagerInterface
from typing import Any
from inventory import inventory_cells_to_ints, ints_to_inventory_cells

SAVES_PATH: str = 'saves'

class SaveManager(SaveManagerInterface):
    def __init__(self, save_name: str) -> None:
        self.save_name = save_name
        self.init_repository()

    def init_repository(self) -> None:
        self.chunks_path = os.path.join(SAVES_PATH, self.save_name, 'chunks')
        self.players_path = os.path.join(SAVES_PATH, self.save_name, 'players')
        self.generation_infos_path = os.path.join(SAVES_PATH, self.save_name, 'generation_infos.json')
        os.makedirs(self.chunks_path, exist_ok=True)
        os.makedirs(self.players_path, exist_ok=True)

    def load_chunk(self, id: int) -> Chunk|None:
        try:
            with open(os.path.join(self.chunks_path, str(id) + '.json')) as f:
                chunk_dict = json.load(f)
        except FileNotFoundError:
            return None
        chunk: Chunk = Chunk(id, chunk_dict['direction'], BIOMES[tuple(chunk_dict['biome'])])
        chunk.is_forest = chunk_dict['is_forest']
        chunk.blocks = int_to_blocks(chunk_dict['blocks'])
        return chunk

    def save_chunk(self, chunk: Chunk|None) -> None:
        if chunk is None: return
        chunk_dict = {
            'direction': chunk.direction,
            'biome': get_biome_environment_values(chunk.biome),
            'is_forest': chunk.is_forest,
            'blocks': blocks_to_int(chunk.blocks)
        }
        with open(os.path.join(self.chunks_path, str(chunk.id) + '.json'), 'w') as f:
            json.dump(chunk_dict, f)
    
    def load_players(self) -> dict[str, dict[str, Any]]|None:
        players: dict[str, dict[str, Any]] = {}
        for player_file in os.listdir(self.players_path):
            try:
                with open(os.path.join(self.players_path, player_file)) as f:
                    player_infos = json.load(f)
                    player_infos['hot_bar_inventory'] = ints_to_inventory_cells(player_infos['hot_bar_inventory'])
                    player_infos['main_inventory'] = ints_to_inventory_cells(player_infos['main_inventory'])
                    players[player_file.removesuffix('.json')] = player_infos
            except FileNotFoundError:
                pass
        return players
    
    def save_players(self, players: list[PlayerInterface]) -> None:
        for player in players:
            player_dict = {
                'direction': player.direction,
                'x': player.x,
                'y': player.y,
                'speed_x': player.speed_x,
                'speed_y': player.speed_y,
                'hot_bar_inventory': inventory_cells_to_ints(player.hot_bar_inventory.cells),
                'main_inventory': inventory_cells_to_ints(player.main_inventory.cells)
            }
            with open(os.path.join(self.players_path, player.name + '.json'), 'w') as f:
                json.dump(player_dict, f)

    def load_generation_infos(self) -> dict[str, Any]|None:
        try:
            with open(self.generation_infos_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return
    
    def save_generation_infos(self, infos: dict[str, Any]) -> None:
        with open(self.generation_infos_path, 'w') as f:
            json.dump(infos, f)