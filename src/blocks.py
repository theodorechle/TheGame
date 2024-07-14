import pygame

class Block:
    BLOCK_SIZE = 10
    PATH = 'src/resources/images/blocks'
    def __init__(self, name) -> None:
        self.name = name
        self.image = None
    
    def load_image(self) -> None:
        try:
            image = pygame.image.load(f'{self.PATH}/{self.name}.png')
        except FileNotFoundError:
            image = pygame.image.load(f'{self.PATH}/unknown.png')
        self.image: pygame.Surface = pygame.transform.scale(image.convert_alpha(),(self.BLOCK_SIZE,self.BLOCK_SIZE))

BLOCKS: list[Block] = [
    Block('air'),
    Block('coal'),
    Block('earth'),
    Block('furnace'),
    Block('grass'),
    Block('iron'),
    Block('lava'),
    Block('leaves'),
    Block('night'),
    Block('plank'),
    Block('sand'),
    Block('stone'),
    Block('torch'),
    Block('wood'),
    Block('workbench')
]
