import blocks
import pygame
from math import ceil
from map_generation import MapGenerator
from map_chunk import Chunk
from save_manager_interface import SaveManagerInterface
from typing import cast

class ChunkManager:
    def __init__(self, nb_chunks_by_side: int, chunk_x_position: int, window: pygame.Surface, map_generator: MapGenerator, save_manager: SaveManagerInterface) -> None:
        self.nb_chunks_by_side: int = 0
        self.chunk_x_position: int = chunk_x_position
        self.window: pygame.Surface = window
        self.map_generator: MapGenerator = map_generator
        self.save_manager: SaveManagerInterface = save_manager
        central_chunk = save_manager.load_chunk(chunk_x_position)
        if central_chunk is None:
            central_chunk = self.map_generator.generate_chunk(False, chunk_x_position)
            self.save_manager.save_chunk(central_chunk)
        self.chunks: list[Chunk] = [central_chunk]
        self.change_nb_chunks(nb_chunks_by_side)
    
    def get_chunk_and_coordinates(self, x: int, y: int) -> tuple[Chunk|None, int, int]:
        if y < 0 or y >= Chunk.HEIGHT: return None, -1, -1
        x += Chunk.LENGTH // 2
        x -= self.chunk_x_position * Chunk.LENGTH
        nb_chunk: int = x // Chunk.LENGTH + self.nb_chunks_by_side
        if nb_chunk < 0 or nb_chunk >= len(self.chunks): return None, -1, -1 # out of loaded chunks
        chunk = self.chunks[nb_chunk]
        return chunk, x % Chunk.LENGTH, y

    def get_block(self, x: int, y: int) -> blocks.Block|None:
        """Return the value at given coordinates, or blocks.NOTHING if out of map"""
        chunk, x, y = self.get_chunk_and_coordinates(x, y)
        if chunk is None: return blocks.NOTHING
        return chunk.blocks[y][x]

    def replace_block(self, x: int, y: int, block: blocks.Block) -> bool:
        chunk, x, y = self.get_chunk_and_coordinates(x, y)
        if chunk is None: return False
        chunk.blocks[y][x] = block
        return True
    
    def update(self, x: int) -> None:
        x += Chunk.LENGTH // 2
        x -= self.chunk_x_position * Chunk.LENGTH
        if x < 0:
            self.change_chunks(-1)
        elif x >= Chunk.LENGTH:
            self.change_chunks(1)

    def change_chunks(self, added_x: int) -> None:
        if added_x == 1:
            self.save_manager.save_chunk(self.chunks.pop(0))
            id = self.chunk_x_position + self.nb_chunks_by_side + 1
            chunk = self.save_manager.load_chunk(id)
            if chunk is None:
                chunk = self.map_generator.generate_chunk(True, id)
            self.chunks.append(chunk)
        else:
            self.save_manager.save_chunk(self.chunks.pop(-1))
            id = self.chunk_x_position - self.nb_chunks_by_side - 1
            chunk = self.save_manager.load_chunk(id)
            if chunk is None:
                chunk = self.map_generator.generate_chunk(False, id)
            self.chunks.insert(0, chunk)
        self.chunk_x_position += added_x

    def change_nb_chunks(self, new_nb_chunks: int) -> None:
        if new_nb_chunks == self.nb_chunks_by_side: return
        new_chunks: list[Chunk|None] = [None for _ in range(new_nb_chunks * 2 + 1)]
        difference = new_nb_chunks - self.nb_chunks_by_side
        if difference > 0:
            for i in range(self.nb_chunks_by_side*2 + 1):
                new_chunks[difference + i] = self.chunks[i]
            for i in range(difference):
                chunk = self.save_manager.load_chunk(self.chunk_x_position - self.nb_chunks_by_side - i - 1)
                if chunk is None:
                    chunk = self.map_generator.generate_chunk(False, self.chunk_x_position - self.nb_chunks_by_side - i - 1)
                    self.save_manager.save_chunk(chunk)
                new_chunks[difference - i - 1] = chunk
                chunk = self.save_manager.load_chunk(self.chunk_x_position + self.nb_chunks_by_side + i + 1)
                if chunk is None:
                    chunk = self.map_generator.generate_chunk(True, self.chunk_x_position + self.nb_chunks_by_side + i + 1)
                    self.save_manager.save_chunk(chunk)
                new_chunks[difference + self.nb_chunks_by_side*2 + 1 + i] = chunk
        else:
            for i in range(new_nb_chunks, self.nb_chunks_by_side):
                self.save_manager.save_chunk(self.chunks[self.nb_chunks_by_side - i - 1])
                self.save_manager.save_chunk(self.chunks[self.nb_chunks_by_side + i + 1])
            for i in range(new_nb_chunks*2 + 1):
                new_chunks[i] = self.chunks[self.nb_chunks_by_side - new_nb_chunks + i]
        
        self.chunks = cast(list[Chunk], new_chunks)
        self.nb_chunks_by_side = new_nb_chunks
    
    def display_chunks(self, x: int, y: int) -> None:
        window_size = self.window.get_size()
        nb_blocks_length = ceil(window_size[0] / blocks.Block.BLOCK_SIZE) + 2
        nb_blocks_height = ceil(window_size[1] / blocks.Block.BLOCK_SIZE) + 2
        for i in range(x - nb_blocks_length // 2, x + nb_blocks_length // 2):
            for j in range(y - nb_blocks_height // 2,  y + nb_blocks_height // 2):
                self.display_block(i, j, -x, -y)
    
    def display_block(self, x: int, y: int, x_add: int, y_add: int) -> None:
        if y < 0 or y >= Chunk.HEIGHT: return
        x += Chunk.LENGTH // 2
        block_x = x - self.chunk_x_position * Chunk.LENGTH
        nb_chunk: int = block_x // Chunk.LENGTH + self.nb_chunks_by_side
        if nb_chunk < 0 or nb_chunk >= len(self.chunks): return # out of loaded chunks
        chunk = self.chunks[nb_chunk]
        block = chunk.blocks[y][block_x % Chunk.LENGTH]
        block_image = block.image
        window_size = self.window.get_size()
        coords = window_size[0] // 2 + blocks.Block.BLOCK_SIZE*(x - Chunk.LENGTH // 2 + x_add - 0.5), window_size[1] // 2 - blocks.Block.BLOCK_SIZE*(y + 1 + y_add)
        self.window.blit(
            blocks.AIR.image,
            coords
        )
        self.window.blit(
            block_image,
            coords
        )

    def save(self) -> None:
        for chunk in self.chunks:
            self.save_manager.save_chunk(chunk)