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

# new blocks must be added to the end in order to not break the exisiting saves
BLOCKS_DICT: dict[Block, int] = {
    AIR: 0,
    EARTH: 1,
    GRASS: 2,
    WOOD: 3,
    LEAVES: 4,
    SAND: 5,
    STONE: 6,
    COAL: 7,
    IRON: 8,
    PLANK: 9,
    LAVA: 10,
    NIGHT: 11,
    TORCH: 12,
    FURNACE: 13,
    WORKBENCH: 14,
    WATER: 15,
    SNOW: 16
}

REVERSED_BLOCKS_DICT: dict[int, Block] = {v: k for k, v in BLOCKS_DICT.items()}

TRAVERSABLE_BLOCKS = [
    AIR,
    WATER,
    LAVA
]

SWIMMABLE_BLOCKS = [
    WATER,
    LAVA
]