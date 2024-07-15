from load_image import load_image

class Block:
    BLOCK_SIZE = 40
    PATH = 'src/resources/images/blocks'
    def __init__(self, name) -> None:
        self.name = name
        self.image = None
    
    def load_image(self) -> None:
        self.image = load_image(f'{self.PATH}/{self.name}.png', (self.BLOCK_SIZE, self.BLOCK_SIZE))

AIR = Block('air')
EARTH = Block('earth')
GRASS = Block('grass')
WOOD = Block('wood')
LEAVES = Block('leaves')
SAND = Block('sand')
STONE = Block('stone')
COAL = Block('coal')
IRON = Block('iron')
PLANK = Block('plank')
LAVA = Block('lava')
NIGHT = Block('night')
TORCH = Block('torch')
FURNACE = Block('furnace')
WORKBENCH = Block('workbench')

BLOCKS: list[Block] = [
    AIR,
    EARTH,
    GRASS,
    WOOD,
    LEAVES,
    SAND,
    STONE,
    COAL,
    IRON,
    PLANK,
    LAVA,
    NIGHT,
    TORCH,
    FURNACE,
    WORKBENCH
]
