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

def blocks_to_int(blocks_list: list[list[blocks.Block]]) -> list[int]:
    """
    Transform a matrix of blocks into a single one-dimensional list of integers
    """
    return [blocks.BLOCKS_DICT[blocks_list[i // len(blocks_list[0])][i % len(blocks_list[0])]] for i in range(len(blocks_list) * len(blocks_list[0]))]


def int_to_blocks(ints: list[int]) -> list[list[blocks.Block]]:
    """
    Transform a list of integers into a matrix of blocks
    """

    return [[blocks.REVERSED_BLOCKS_DICT[ints[x + y * Chunk.LENGTH]] for x in range(Chunk.LENGTH)] for y in range(Chunk.HEIGHT)]

