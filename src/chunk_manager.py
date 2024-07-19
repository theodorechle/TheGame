import blocks
import pygame
from math import trunc, ceil
import blocks

class Chunk:
    LENGTH = 16
    HEIGHT = 32
    def __init__(self, id) -> None:
        self.id = id
        self.chunk = None
        self.load()
    
    def load(self):
        self.chunk: list[list[blocks.Block]] = [[blocks.STONE for x in range(self.LENGTH)] for y in range(self.HEIGHT//2, self.HEIGHT)] \
                + [[blocks.AIR for x in range(self.LENGTH)] for y in range(self.HEIGHT//2)] # temp, for tests
    
    def unload(self):
        ...

class ChunkManager:
    def __init__(self, nb_chunks_by_side, chunk_x_position, window: pygame.Surface) -> None:
        self.nb_chunks_by_side = 0
        self.chunk_x_position = chunk_x_position
        self.window = window
        self.chunks: list[Chunk] = [Chunk(chunk_x_position)]
        self.change_nb_chunks(nb_chunks_by_side)
    
    def get_chunk_and_coordinates(self, x: int, y: int) -> tuple[Chunk, int, int]:
        if y < 0 or y >= Chunk.HEIGHT: return None, -1, -1
        x += Chunk.LENGTH // 2
        if self.chunk_x_position != 0:
            x %= abs(self.chunk_x_position) * Chunk.LENGTH
        nb_chunk: int = x // Chunk.LENGTH + self.nb_chunks_by_side
        if nb_chunk < 0 or nb_chunk >= len(self.chunks): return None, -1, -1 # out of loaded chunks
        chunk = self.chunks[nb_chunk]
        return chunk, x % Chunk.LENGTH, y

    def get_block(self, x: int, y: int) -> blocks.Block:
        """Return the value at given coordinates, or -1 if out of map"""
        chunk, x, y = self.get_chunk_and_coordinates(x, y)
        if chunk is None: return -1
        return chunk.chunk[y][x]

    def replace_block(self, x: int, y: int, block: blocks.Block) -> bool:
        chunk, x, y = self.get_chunk_and_coordinates(x, y)
        if chunk is None: return False
        chunk.chunk[y][x] = block
        return True

    def change_nb_chunks(self, new_nb_chunks: int) -> None:
        new_chunks = [None for _ in range(new_nb_chunks * 2 + 1)]
        difference = new_nb_chunks - self.nb_chunks_by_side
        if difference > 0:
            for i in range(self.nb_chunks_by_side*2 + 1):
                new_chunks[difference + i] = self.chunks[i]
            for i in range(difference):
                new_chunks[i] = Chunk(self.chunk_x_position - self.nb_chunks_by_side + i)
                new_chunks[new_nb_chunks + i + 1] = Chunk(self.chunk_x_position + self.nb_chunks_by_side + i)
            if new_chunks[new_nb_chunks] is None: # central chunk
                new_chunks[new_nb_chunks] = Chunk(self.chunk_x_position)
        else:
            for i in range(difference):
                self.chunks[i].unload()
                self.chunks[self.nb_chunks_by_side - i].unload()
            for i in range(new_nb_chunks*2 + 1):
                new_chunks[i] = self.chunks[difference + i]
        self.chunks = new_chunks
        self.nb_chunks_by_side = new_nb_chunks
    
    def display_chunks(self, x: int, y: int) -> None:
        window_size = self.window.get_size()
        nb_blocks_length = ceil(window_size[0] / blocks.Block.BLOCK_SIZE)
        nb_blocks_height = ceil(window_size[1] / blocks.Block.BLOCK_SIZE)
        for i in range(trunc(x) - nb_blocks_length // 2, ceil(x) + nb_blocks_length // 2 + 1):
            for j in range(trunc(y) - nb_blocks_height // 2,  ceil(y) + nb_blocks_height // 2 + 1):
                self.display_block(i, j, -x, -y)
    
    def display_block(self, x: int, y: int, x_add: int, y_add: int) -> None:
        if y < 0 or y >= Chunk.HEIGHT: return
        x += Chunk.LENGTH // 2
        if self.chunk_x_position != 0:
            x %= abs(self.chunk_x_position) * Chunk.LENGTH
        nb_chunk: int = x // Chunk.LENGTH + self.nb_chunks_by_side
        if nb_chunk < 0 or nb_chunk >= len(self.chunks): return # out of loaded chunks
        chunk = self.chunks[nb_chunk]
        block = chunk.chunk[y][x % Chunk.LENGTH]
        block_image = block.image
        window_size = self.window.get_size()
        self.window.blit(
            block_image,
            (window_size[0] // 2 + blocks.Block.BLOCK_SIZE*(x - Chunk.LENGTH // 2 + x_add - 0.5),
             window_size[1] // 2 - blocks.Block.BLOCK_SIZE*(y + 1 + y_add))
        )

