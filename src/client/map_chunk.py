import blocks
from generation.biomes import Biome
import pygame

class Chunk:
    LENGTH: int = 32
    HEIGHT: int = 128
    def __init__(self, id: int, biome: Biome, is_forest: bool=False) -> None:
        """direction: False -> left, True -> right"""
        self.id: int = id
        self.biome: Biome = biome
        self.is_forest: bool = is_forest
        self.blocks: list[blocks.Block] = []
        self.reset_display_surface()
    
    def set_diffs(self, diffs: dict[int, int]) -> None:
        for index, block in diffs.items():
            self.blocks[int(index)] = blocks.REVERSED_BLOCKS_DICT[block]

    def update_display_surface(self) -> None:
        for index, block in enumerate(self.blocks):
            coords = ((index % Chunk.LENGTH) * blocks.block_size, (Chunk.HEIGHT - (index // Chunk.LENGTH)) * blocks.block_size)
            self._diplay_surface.blits(
                ((blocks.AIR.image, coords),
               (block.image, coords))
            )
    
    def reset_display_surface(self) -> None:
        self._diplay_surface: pygame.Surface = pygame.Surface((self.LENGTH * blocks.block_size, self.HEIGHT * blocks.block_size))
        self.update_display_surface()

    def replace_block(self, index: int, block: blocks.Block) -> None:
        self.blocks[index] = block
        coords = (index % Chunk.LENGTH) * blocks.block_size, (Chunk.HEIGHT - index // Chunk.LENGTH) * blocks.block_size
        self._diplay_surface.blits(
            ((blocks.AIR.image, coords),
            (block.image, coords))
        )
    
    def display_chunk(self, coords: tuple[int, int], surface: pygame.Surface) -> None:
        surface.blit(self._diplay_surface, coords)

    def __repr__(self) -> str:
        return f'id: {self.id}, biome: {self.biome.name}, is_forest: {self.is_forest}'
