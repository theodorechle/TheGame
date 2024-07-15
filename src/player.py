from load_image import load_image
import chunk_manager
from pygame import Surface
import blocks

class Inventory:
    def __init__(self, nb_cells: int) -> None:
        self.nb_cells = nb_cells
        self.cells: list[tuple[int, int]] = [(-1, 0) for _ in range(self.nb_cells)] # list of tuples with

class Player:
    PLAYER_SIZE = (1, 2) # number of blocks width and height
    image_size = (PLAYER_SIZE[0] * blocks.Block.BLOCK_SIZE, PLAYER_SIZE[1] * blocks.Block.BLOCK_SIZE)
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
        self.chunk_manager.chunks[3].chunk[15][8] = blocks.GRASS
        self.chunk_manager.chunks[0].chunk[16][0] = blocks.COAL
        self.chunk_manager.chunks[0].chunk[15][1] = blocks.IRON
        self.image = None
        self.image_reversed = None
        self.direction = False # False if right, True if left
    
    def load_image(self) -> None:
        self.image = load_image(f'{self.PATH}/{self.name}.png', self.image_size)
        self.image_reversed = load_image(f'{self.PATH}/{self.name}_reversed.png', self.image_size)
    
    def display(self) -> None:
        window_size = self.window.get_size()
        self.window.blit(
            self.image_reversed if self.direction else self.image,
            (window_size[0] // 2 - blocks.Block.BLOCK_SIZE // 2,
             window_size[1] // 2 - self.image_size[1])
        )

    def update(self) -> None:
        is_valid_pos = True
        for x in range(self.PLAYER_SIZE[0]):
            block = self.chunk_manager.get_block(self.x + x, self.y - 1)
            if block == -1 or block != blocks.AIR:
                is_valid_pos = False
                break
        if is_valid_pos:
            self.y -= 1
        if not self.speed_x: return
        sign = (1 if self.speed_x >= 0 else -1)
        new_direction = (sign == -1)
        if new_direction != self.direction:
            self.direction = new_direction
        else:
            for _ in range(abs(self.speed_x)):
                is_valid_pos = True
                for y in range(self.PLAYER_SIZE[1]):
                    block = self.chunk_manager.get_block(self.x + self.PLAYER_SIZE[0] * sign, self.y + y)
                    if block == -1 or block != blocks.AIR:
                        is_valid_pos = False
                        break
                if is_valid_pos:
                    self.x += sign
        self.speed_x = sign * (abs(self.speed_x) // 2)

    def save(self) -> None:
        ...
    
    def place_block(self, pos: tuple[int, int]) -> None:
        x = (pos[0] - self.window.get_size()[0] // 2 + blocks.Block.BLOCK_SIZE // 2) // blocks.Block.BLOCK_SIZE
        y = -(pos[1] - self.window.get_size()[1] // 2) // blocks.Block.BLOCK_SIZE
        if 0 <= y < self.PLAYER_SIZE[1]: # left or right
            if self.direction:
                if x != -1:
                    return
            else:
                if x != self.PLAYER_SIZE[0]:
                    return
        elif y == -1 or y == self.PLAYER_SIZE[1]: # down or up
            if not (0 <= x < self.PLAYER_SIZE[0]):
                return
        else:
            return
        block = self.chunk_manager.get_block(self.x + x, self.y + y)
        if block == blocks.AIR:
            self.chunk_manager.replace_block(self.x + x, self.y + y, blocks.GRASS)

    def remove_block(self, pos: tuple[int, int]) -> None:
        x = (pos[0] - self.window.get_size()[0] // 2 + blocks.Block.BLOCK_SIZE // 2) // blocks.Block.BLOCK_SIZE
        y = -(pos[1] - self.window.get_size()[1] // 2) // blocks.Block.BLOCK_SIZE
        if 0 <= y < self.PLAYER_SIZE[1]: # left or right
            if self.direction:
                if x != -1:
                    return
            else:
                if x != self.PLAYER_SIZE[0]:
                    return
        elif y == -1 or y == self.PLAYER_SIZE[1]: # down or up
            if not (0 <= x < self.PLAYER_SIZE[0]):
                return
        else:
            return
        block = self.chunk_manager.get_block(self.x + x, self.y + y)
        if block != blocks.AIR:
            self.chunk_manager.replace_block(self.x + x, self.y + y, blocks.AIR)
