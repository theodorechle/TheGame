from load_image import load_image
import chunk_manager
from pygame import Surface
from blocks import Block

class Player:
    PLAYER_SIZE = (Block.BLOCK_SIZE, Block.BLOCK_SIZE * 2)
    PATH = 'src/resources/images/persos'
    def __init__(self, name: str, x: int, y: int, speed_x: float, speed_y: float, window: Surface) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.window = window
        self.render_distance = 3
        self.chunk_manager = chunk_manager.ChunkManager(3, 0, window)
        self.chunk_manager.chunks[3].chunk[15][8] = 4
        self.chunk_manager.chunks[0].chunk[15][0] = 1
        self.image = None
    
    def load_image(self) -> None:
        self.image = load_image(f'{self.PATH}/{self.name}.png', self.PLAYER_SIZE)
    
    def display(self) -> None:
        window_size = self.window.get_size()
        self.window.blit(self.image, (window_size[0] // 2 - self.PLAYER_SIZE[0] // 2, window_size[1] // 2 - self.PLAYER_SIZE[1]))
