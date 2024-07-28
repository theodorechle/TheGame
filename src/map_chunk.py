from blocks import Block
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
        self.blocks: list[list[Block]] = []

