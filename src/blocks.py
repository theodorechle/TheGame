import pygame

class Block:
    BLOCK_SIZE = 50
    PATH = 'resources/images/blocks'
    def __init__(self, name) -> None:
        self.name = name
        try:
            image = pygame.image.load(f'{self.PATH}/{self.name}.png')
        except FileNotFoundError:
            image = pygame.image.load(f'{self.PATH}/unknown.png')
        self.image = pygame.transform.scale(image.convert_alpha(),(self.BLOCK_SIZE,self.BLOCK_SIZE))

BLOCKS = [
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
