from map_chunk import Chunk, blocks_to_int, int_to_blocks
import json
import os
from biomes import BIOMES, get_biome_environment_values

class SaveManager:
    PATH = 'saves'
    def __init__(self, save_name: str) -> None:
        self.save_name = save_name
        self.init_repository()

    def init_repository(self) -> None:
        path = f'{self.PATH}/{self.save_name}/chunks'
        os.makedirs(path, exist_ok=True)

    def load_chunk(self, id: int) -> Chunk|None:
        try:
            with open(f'{self.PATH}/{self.save_name}/chunks/{id}.json') as f:
                chunk_dict = json.load(f)
            chunk: Chunk = Chunk(id, chunk_dict['direction'], BIOMES[tuple(chunk_dict['biome'])])
            chunk.is_forest = chunk_dict['is_forest']
            chunk.blocks = int_to_blocks(chunk_dict['blocks'])
            return chunk
        except FileNotFoundError:
            return None
    
    def save_chunk(self, chunk: Chunk|None) -> None:
        if chunk is None: return
        chunk_dict = {
            'direction': chunk.direction,
            'biome': get_biome_environment_values(chunk.biome),
            'is_forest': chunk.is_forest,
            'blocks': blocks_to_int(chunk.blocks)
        }
        with open(f'{self.PATH}/{self.save_name}/chunks/{chunk.id}.json', 'w') as f:
            json.dump(chunk_dict, f)