from load_image import load_image

class Block:
    BLOCK_SIZE = 30
    PATH = 'src/resources/images/blocks'
    def __init__(self, name: str) -> None:
        self.name = name
        self.image = load_image([f'{self.PATH}/{self.name}.png'], (self.BLOCK_SIZE, self.BLOCK_SIZE))
    
    def __repr__(self) -> str:
        return self.name

NOTHING = None
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
WATER = Block('water')
SNOW = Block('snow')

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
    WORKBENCH,
    WATER,
    SNOW
]

TRAVERSABLE_BLOCKS = [
    AIR,
    WATER,
    LAVA
]

SWIMMABLE_BLOCKS = [
    WATER,
    LAVA
]