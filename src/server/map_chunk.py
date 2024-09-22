import blocks
from generation.biomes import Biome, get_biome_environment_values

class Chunk:
    LENGTH: int = 32
    HEIGHT: int = 128
    def __init__(self, id: int, direction: bool, biome: Biome) -> None:
        """direction: False -> left, True -> right"""
        self.id: int = id
        self.direction: bool = direction
        self.biome: Biome = biome
        self.is_forest: bool = False
        self.blocks: list[blocks.Block] = []
        self.diffs: set[int] = set()

    def get_infos_dict(self) -> dict:
        return {
            'id': self.id,
            'diffs': list(self.diffs)
        }
    
    def get_all_infos_dict(self) -> dict:
        return {
            'id': self.id,
            'biome': self.biome.name,
            'is-forest': self.is_forest,
            'diffs': list(self.diffs)
        }
        
    def __repr__(self) -> str:
        return f'id: {self.id}, direction: {self.direction}, biome: {self.biome.name}, is_forest: {self.is_forest}'
