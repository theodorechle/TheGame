from load_image import load_image
import chunk_manager
from pygame import Surface
from blocks import Block, BLOCKS

class Player:
    PLAYER_SIZE = (Block.BLOCK_SIZE, Block.BLOCK_SIZE * 2)
    PATH = 'src/resources/images/persos'
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, window: Surface) -> None:
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
        self.window.blit(
            self.image,
            (window_size[0] // 2 - self.PLAYER_SIZE[0] // 2,
             window_size[1] // 2 - self.PLAYER_SIZE[1])
        )

    def update(self) -> None:
        for x in range(abs(self.speed_x)):
            if BLOCKS[self.chunk_manager.get_block(self.x + x, self.y)].name == 'air':
                self.x += (1 if self.speed_x >= 0 else -1)
        self.speed_x = (1 if self.speed_x >= 0 else -1) * (abs(self.speed_x) // 2)
