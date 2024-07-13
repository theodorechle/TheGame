import blocks

class Chunk:
    LENGTH = 16
    HEIGHT = 32
    def __init__(self, id) -> None:
        self.id = id
        self.load()
    
    def load(self):
        self.chunk = [[0 for x in range(self.LENGTH)] for y in range(self.HEIGHT//2, self.HEIGHT-(self.HEIGHT//2))] \
                + [[11 for x in range(self.LENGTH)] for y in range(self.HEIGHT//2)] # temp, for tests
    
    def unload(self):
        ...
    
    def replace_block(self, x: int, y: int, block: int):
        if 0 <= x < self.LENGTH \
                and 0 <= y < self.HEIGHT:
            self.chunk[y][x] = block
    
    

class ChunkManager:
    def __init__(self, nb_chunks_by_side, chunk_id) -> None:
        self.nb_chunks_by_side = 0
        self.chunk_id = chunk_id
        self.chunks: list[Chunk] = []
        self.change_nb_chunks(nb_chunks_by_side)
    
    def change_nb_chunks(self, new_nb_chunks: int) -> None:
        new_chunks = [None for _ in range(new_nb_chunks)]
        difference = new_nb_chunks - self.nb_chunks_by_side
        if difference > 0:
            for i in range(self.nb_chunks_by_side*2 + 1):
                new_chunks[difference + i] = self.chunks[i]
            for i in range(difference):
                new_chunks[self.nb_chunks_by_side + i] = Chunk(self.chunk_id + self.nb_chunks_by_side + i)
                new_chunks[i] = Chunk(self.chunk_id - self.nb_chunks_by_side + i)
        else:
            for i in range(difference):
                self.chunks[i].unload()
                self.chunks[self.nb_chunks_by_side - i].unload()
            for i in range(new_nb_chunks*2 + 1):
                new_chunks[i] = self.chunks[difference + i]
        self.chunks = new_chunks
        self.nb_chunks_by_side = new_nb_chunks
    
    