import blocks
from map_chunk import Chunk
from logs import write_log
from map_generation import MapGenerator
from save_manager import SaveManager

class ChunkManager:
    def __init__(self, map_generator: MapGenerator, save_manager: SaveManager) -> None:
        self.map_generator = map_generator
        self.save_manager = save_manager
        self.chunks: dict[int, Chunk] = {}
    
    def get_chunk_and_coordinates(self, x: int, y: int) -> tuple[Chunk|None, int, int]:
        if y < 0 or y >= Chunk.HEIGHT: return None, -1, -1
        x += Chunk.LENGTH // 2
        nb_chunk: int = x // Chunk.LENGTH
        if nb_chunk not in self.chunks: return None, -1, -1 # not in loaded chunks
        return self.chunks[nb_chunk], x % Chunk.LENGTH, y

    def get_block(self, x: int, y: int) -> int:
        """Return the value at given coordinates, or blocks.NOTHING if out of map"""
        chunk, x, y = self.get_chunk_and_coordinates(x, y)
        if chunk is None: return blocks.NOTHING
        return chunk.blocks[y][x]

    def replace_block(self, x: int, y: int, block: int) -> bool:
        chunk, x, y = self.get_chunk_and_coordinates(x, y)
        if chunk is None: return False
        chunk.blocks[y][x] = block
        return True
    
    # def update(self, x: int) -> None:
    #     x += Chunk.LENGTH // 2
    #     x -= self.chunk_x_position * Chunk.LENGTH
    #     if x < 0:
    #         self.change_chunks(-1)
    #     elif x >= Chunk.LENGTH:
    #         self.change_chunks(1)

    def save(self) -> None:
        for chunk in self.chunks:
            self.save_manager.save_chunk(chunk)
    
    def load_chunk(self, chunk_id: int) -> Chunk|None:
        if chunk_id in self.chunks:
            return self.chunks[chunk_id]
        chunk = self.save_manager.load_chunk(chunk_id)
        if chunk is None:
            chunk = self.map_generator.generate_chunk(chunk_id)
            if chunk is None:
                write_log(f'Chunk {chunk_id} was not generated', True)
                return None
        self.chunks[chunk_id] = chunk
        return chunk
