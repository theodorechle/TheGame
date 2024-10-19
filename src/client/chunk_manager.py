import blocks
import pygame
from map_chunk import Chunk
from server_connection import ServerConnection
from generation.map_generation import MapGenerator
from typing import Any

class ChunkManager:
    def __init__(self, chunk_x_position: int, window: pygame.Surface, server: ServerConnection) -> None:
        self.nb_chunks_by_side: int = 0
        self.chunk_x_position: int = chunk_x_position
        self.window: pygame.Surface = window
        self.server = server
        self.chunks: list[Chunk|None] = [None]
        self.map_generator = None
    
    async def initialize_chunks(self, nb_chunks_by_side: int) -> None:
        await self.initialize_map_generator()
        await self.load_chunk(0)
        await self.change_nb_chunks(nb_chunks_by_side)
    
    async def initialize_map_generator(self) -> None:
        await self.server.send_json({
            'method': 'GET',
            'data': {
                'type': 'game-infos'
            }
        })

    def create_map_generator(self, data: dict[str, Any]) -> None:
        self.map_generator = MapGenerator(data['infos']['seed'])

    def get_chunk_and_block_index(self, x: int, y: int) -> tuple[Chunk|None, int]:
        if y < 0 or y >= Chunk.HEIGHT: return None, -1
        x += Chunk.LENGTH // 2
        x -= self.chunk_x_position * Chunk.LENGTH
        nb_chunk: int = x // Chunk.LENGTH + self.nb_chunks_by_side
        if nb_chunk < 0 or nb_chunk >= len(self.chunks): return None, -1 # out of loaded chunks
        chunk = self.chunks[nb_chunk]
        return chunk, (x % Chunk.LENGTH) + y * Chunk.LENGTH

    def get_block(self, x: int, y: int)  -> blocks.Block|None:
        """Return the value at given coordinates, or blocks.NOTHING if out of map"""
        chunk, index = self.get_chunk_and_block_index(x, y)
        if chunk is None: return blocks.NOTHING
        return chunk.blocks[index]

    def replace_block(self, x: int, y: int, block: blocks.Block) -> bool:
        chunk, index = self.get_chunk_and_block_index(x, y)
        if chunk is None: return False
        chunk.replace_block(index, block)
        return True
    
    async def update(self, x: int) -> None:
        x += Chunk.LENGTH // 2
        x -= self.chunk_x_position * Chunk.LENGTH
        if x < 0:
            await self.change_chunks(-1)
        elif x >= Chunk.LENGTH:
            await self.change_chunks(1)

    async def change_chunks(self, added_x: int) -> None:
        if added_x == 1:
            self.chunks.pop(0)
            id = self.chunk_x_position + self.nb_chunks_by_side + 1
            self.chunks.append(None)
            await self.load_chunk(id)
            await self.save_chunks([self.chunk_x_position - self.nb_chunks_by_side])
        else:
            self.chunks.pop(-1)
            id = self.chunk_x_position - self.nb_chunks_by_side - 1
            self.chunks.insert(0, None)
            await self.load_chunk(id)
            await self.save_chunks([self.chunk_x_position + self.nb_chunks_by_side])
        self.chunk_x_position += added_x

    async def change_nb_chunks(self, new_nb_chunks: int) -> None:
        if new_nb_chunks == self.nb_chunks_by_side: return
        new_chunks: list[Chunk|None] = [None for _ in range(new_nb_chunks * 2 + 1)]
        difference = new_nb_chunks - self.nb_chunks_by_side
        if difference > 0:
            for i in range(self.nb_chunks_by_side*2 + 1):
                new_chunks[difference + i] = self.chunks[i]
            for i in range(difference):
                await self.load_chunk(self.chunk_x_position - self.nb_chunks_by_side - i - 1)
                await self.load_chunk(self.chunk_x_position + self.nb_chunks_by_side + i + 1)
        else:
            await self.save_chunks([nb + self.chunk_x_position for i in range(new_nb_chunks, self.nb_chunks_by_side) for nb in (-i - 1, i + 1)])
            for i in range(new_nb_chunks*2 + 1):
                new_chunks[i] = self.chunks[self.nb_chunks_by_side - new_nb_chunks + i]
        
        self.chunks = new_chunks
        self.nb_chunks_by_side = new_nb_chunks
    
    def display_chunks(self, x: int, y: int) -> None:
        window_size = self.window.get_size()
        for index, chunk in enumerate(self.chunks):
            if chunk is None: continue
#             coords = window_size[0] // 2 + blocks.block_size*(index + x - 0.5), window_size[1] // 2 - blocks.block_size*(index + y + 1)
            coords: tuple[float, float] = (((index + self.chunk_x_position - self.nb_chunks_by_side - 0.5) * Chunk.LENGTH - x - 0.5) * blocks.block_size + window_size[0] // 2, window_size[1] // 2 - (Chunk.HEIGHT - y) * blocks.block_size)
            chunk.display_chunk(coords, self.window)

    # def display_chunks(self, x: int, y: int) -> None:
    #     window_size = self.window.get_size()
    #     nb_blocks_length = ceil(window_size[0] / blocks.block_size + 2)
    #     nb_blocks_height = ceil(window_size[1] / blocks.block_size + 2)
    #     # display the minimum between the window size and the number of loaded blocks
    #     min_x = max(x - nb_blocks_length // 2, (self.chunk_x_position - self.nb_chunks_by_side) * Chunk.LENGTH - Chunk.LENGTH // 2)
    #     max_x = min(x + nb_blocks_length // 2, (self.chunk_x_position + self.nb_chunks_by_side) * Chunk.LENGTH + Chunk.LENGTH // 2)
    #     min_y = max(0, y - nb_blocks_height // 2)
    #     max_y = min(Chunk.HEIGHT, y + nb_blocks_height // 2)
    #     for i in range(min_x, max_x):
    #         for j in range(min_y, max_y):
    #             self.display_block(i, j, -x, -y)
    
    # def display_block(self, x: int, y: int, x_add: int, y_add: int) -> None:
    #     block_x = x + Chunk.LENGTH // 2 - self.chunk_x_position * Chunk.LENGTH
    #     index = block_x // Chunk.LENGTH + self.nb_chunks_by_side
    #     if index < 0 or index >= len(self.chunks): return
    #     chunk = self.chunks[index]
    #     if chunk is None:
    #         return
    #     window_size = self.window.get_size()
    #     coords = window_size[0] // 2 + blocks.block_size*(x + x_add - 0.5), window_size[1] // 2 - blocks.block_size*(y + 1 + y_add)
    #     self.window.blits(
    #         ((blocks.AIR.image, coords), (chunk.blocks[y * Chunk.LENGTH + block_x % Chunk.LENGTH].image, coords))
    #     )

    async def load_chunk(self, chunk_id: int) -> None:
        await self.server.send_json({
            'method': 'GET',
            'data': {
                'type': 'chunk',
                'id': chunk_id
            }
        })
    
    async def save_chunks(self, chunks_ids: list[int]) -> None:
        await self.server.send_json({
            'method': 'POST',
            'data': {
                'type': 'chunks',
                'ids': chunks_ids
            }
        })
    
    def set_chunk_surface(self, id: int) -> None:
        index = id - self.chunk_x_position + self.nb_chunks_by_side
        if self.chunks[index] is None: return
        self.chunks[index].update_display_surface()
        
    def scale_chunk_surfaces(self) -> None:
        for chunk in self.chunks:
            if chunk is None: continue
            chunk.reset_display_surface()

    def set_chunk(self, message: dict[str, Any]) -> None:
        if not message or message['status'] == ServerConnection.WRONG_REQUEST:
            return
        chunk_infos = message['data']['chunk']
        id = chunk_infos['id']
        index = id - self.chunk_x_position + self.nb_chunks_by_side
        self.chunks[index] = self.map_generator.generate_chunk(id)
        self.chunks[index].set_diffs(chunk_infos['diffs'])
        self.set_chunk_surface(id)