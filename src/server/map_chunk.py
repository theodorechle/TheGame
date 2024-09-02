import blocks
from biomes import Biome

class Chunk:
    LENGTH: int = 32
    HEIGHT: int = 128
    def __init__(self, id: int, direction: bool, biome: Biome) -> None:
        """direction: False -> left, True -> right"""
        self.id: int = id
        self.direction: bool = direction
        self.biome: Biome = biome
        self.is_forest: bool = False
        self.blocks: list[list[blocks.Block]] = []
    
    def __repr__(self) -> str:
        return f'id: {self.id}, direction: {self.direction}, biome: {self.biome.name}, is_forest: {self.is_forest}'

