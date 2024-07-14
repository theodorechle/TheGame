from load_image import load_image

class Block:
    BLOCK_SIZE = 40
    PATH = 'src/resources/images/blocks'
    def __init__(self, name) -> None:
        self.name = name
        self.image = None
    
    def load_image(self) -> None:
        self.image = load_image(f'{self.PATH}/{self.name}.png', (self.BLOCK_SIZE, self.BLOCK_SIZE))

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
