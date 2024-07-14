from pygame import Surface
import chunk_manager

class Player:
    def __init__(self, x, y, speed_x, speed_y, window: Surface) -> None:
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.window = window
        self.render_distance = 3
        self.chunk_manager = chunk_manager.ChunkManager(3, 0, window)
        self.chunk_manager.chunks[3].chunk[15][8] = 4
        self.chunk_manager.chunks[0].chunk[15][0] = 1

    
    