import blocks
from generation.biomes import Biome

class Chunk:
    LENGTH: int = 32
    HEIGHT: int = 128
    def __init__(self, id: int, biome: Biome, is_forest: bool=False) -> None:
        """direction: False -> left, True -> right"""
        self.id: int = id
        self.biome: Biome = biome
        self.is_forest: bool = is_forest
        self.blocks: list[blocks.Block] = []
        self.diffs = set()
    
    def __repr__(self) -> str:
        return f'id: {self.id}, biome: {self.biome.name}, is_forest: {self.is_forest}'

def ints_to_blocks(ints: list[int]) -> list[blocks.Block]:
    """
    Transform a list of integers into a list of blocks
    """

    return [blocks.REVERSED_BLOCKS_DICT[ints[index]] for index in range(Chunk.LENGTH * Chunk.HEIGHT)]

