from pygame import Surface
import chunk

class Player:
    def __init__(self, x, y, speed_x, speed_y, window: Surface) -> None:
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.window = window
        self.render_distance = 3
        self.chunk_manager = chunk.ChunkManager(3, 0, window)
        self.chunk_manager.display_chunks(self.x, self.y)
    
    