import blocks
from map_chunk import Chunk
from logs import write_log
from generation.map_generation import MapGenerator
from save_manager import SaveManager

class ChunkManager:
    def __init__(self, map_generator: MapGenerator, save_manager: SaveManager) -> None:
        self.map_generator = map_generator
        self.save_manager = save_manager
        self.chunks: dict[int, Chunk] = {}
        self.nb_players_who_loaded_chunks: dict[int, int] = {}
        self.loaded_chunks_by_player: dict[str, set[int]] = {}
    
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
        return chunk.blocks[y * Chunk.LENGTH + x]

    def replace_block(self, x: int, y: int, block: int) -> bool:
        chunk, x, y = self.get_chunk_and_coordinates(x, y)
        if chunk is None: return False
        chunk.replace_block(y * Chunk.LENGTH + x, block)
        return True

    def save_chunks(self, player_name: str, chunks_ids: list[int]) -> None:
        if player_name not in self.loaded_chunks_by_player: return
        loaded_chunks: set[int] = self.loaded_chunks_by_player[player_name]
        for chunk_id in chunks_ids:
            if chunk_id not in loaded_chunks: continue
            loaded_chunks.remove(chunk_id)
            self.nb_players_who_loaded_chunks[chunk_id] -= 1
            if self.nb_players_who_loaded_chunks[chunk_id] == 0:
                self.nb_players_who_loaded_chunks.pop(chunk_id)
                self.save_manager.save_chunk(self.chunks[chunk_id])
                self.chunks.pop(chunk_id)
    
    def load_chunk(self, player_name: str, chunk_id: int) -> Chunk|None:
        if player_name not in self.loaded_chunks_by_player:
            self.loaded_chunks_by_player[player_name] = set()
        loaded_chunks: set[int] = self.loaded_chunks_by_player[player_name]
        if chunk_id in loaded_chunks: return
        loaded_chunks.add(chunk_id)
        if chunk_id not in self.nb_players_who_loaded_chunks:
            self.nb_players_who_loaded_chunks[chunk_id] = 1
        else:
            self.nb_players_who_loaded_chunks[chunk_id] += 1
        if chunk_id in self.chunks: return self.chunks[chunk_id]
        loaded = self.save_manager.load_chunk(chunk_id)
        if isinstance(loaded, Chunk):
            chunk = loaded
        else:
            chunk = self.map_generator.generate_chunk(chunk_id)
            if chunk is None:
                write_log(f'Chunk {chunk_id} was not generated', True)
                return
            if isinstance(loaded, dict):
                for index, block in loaded.items():
                    chunk.replace_block(int(index), block)
        self.chunks[chunk_id] = chunk
        return chunk
