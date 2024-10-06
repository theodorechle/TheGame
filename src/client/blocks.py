from module_infos import RESOURCES_PATH
BLOCKS_IMAGES_PATH = f'{RESOURCES_PATH}/images/blocks'

from load_image import load_image
from pygame import Surface
from blocks_menus.workbench_menu import WorkbenchMenu
from blocks_menus.furnace_menu import FurnaceMenu

block_size = 30

class Block:
    def __init__(self, name: str) -> None:
        self.name = name
        self.load_image()
    
    def load_image(self):
        self.image: Surface = load_image([f'{BLOCKS_IMAGES_PATH}/{self.name}.png'], (block_size, block_size))
    
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

# new blocks must be added to the end in order to not break the existing saves
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

INTERACTABLE_BLOCKS = {
    WORKBENCH: WorkbenchMenu,
    # FURNACE: FurnaceMenu
}