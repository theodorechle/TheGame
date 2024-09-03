import blocks

class Chunk:
    LENGTH: int = 32
    HEIGHT: int = 128
    def __init__(self, id: int, biome: str, is_forest: bool=False, blocks: list[list[blocks.Block]]|None=None) -> None:
        """direction: False -> left, True -> right"""
        self.id: int = id
        self.biome: str = biome
        self.is_forest: bool = is_forest
        if blocks is not None and len(blocks) == self.HEIGHT and len(blocks[0]) == self.LENGTH:
            self.blocks: list[list[blocks.Block]] = blocks
        else:
            self.blocks: list[list[blocks.Block]] = []
    
    def __repr__(self) -> str:
        return f'id: {self.id}, biome: {self.biome}, is_forest: {self.is_forest}'

def int_to_blocks(ints: list[int]) -> list[list[blocks.Block]]:
    """
    Transform a list of integers into a matrix of blocks
    """

    return [[blocks.REVERSED_BLOCKS_DICT[ints[y][x]] for x in range(Chunk.LENGTH)] for y in range(Chunk.HEIGHT)]

