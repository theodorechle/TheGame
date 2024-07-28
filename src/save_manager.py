from map_chunk import Chunk

class SaveManager:
    def load_chunk(self, id: int) -> Chunk|None:
        ...
    
    def save_chunk(self, chunk: Chunk) -> None:
        ...
    