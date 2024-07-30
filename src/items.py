from load_image import load_image
from blocks import BLOCKS_IMAGES_PATH

ITEMS_IMAGES_PATH = 'src/resources/images/items'
class Item:
    ITEM_SIZE = 20
    def __init__(self, name: str) -> None:
        self.name = name
        self.image = load_image([f'{ITEMS_IMAGES_PATH}/{self.name}.png', f'{BLOCKS_IMAGES_PATH}/{self.name}.png'], (self.ITEM_SIZE, self.ITEM_SIZE))
        self.stack_size = 99
    
    def __repr__(self) -> str:
        return self.name

NOTHING = None
IRON_INGOT = Item('iron_ingot')
STICK = Item('stick')
STONE_PICKAXE = Item('stone_pickaxe')
IRON_PICKAXE = Item('iron_pickaxe')
LAVA_BUCKET = Item('lava_bucket')
EARTH = Item('earth')
GRASS = Item('grass')
WOOD = Item('wood')
SAND = Item('sand')
STONE = Item('stone')
COAL = Item('coal')
IRON = Item('iron')
PLANK = Item('plank')
TORCH = Item('torch')
FURNACE = Item('furnace')
WORKBENCH = Item('workbench')
SNOW = Item('snow')

# new items must be added to the end in order to not break the exisiting saves
ITEMS_DICT: dict[Item, int] = {
    IRON_INGOT: 0,
    STICK: 1,
    STONE_PICKAXE: 2,
    IRON_PICKAXE: 3,
    LAVA_BUCKET: 4,
    EARTH: 5,
    GRASS: 6,
    WOOD: 7,
    SAND: 8,
    STONE: 9,
    COAL: 10,
    IRON: 11,
    PLANK: 12,
    TORCH: 13,
    FURNACE: 14,
    WORKBENCH: 15,
    SNOW: 16
}

REVERSED_ITEMS_DICT: dict[int, Item] = {v: k for k, v in ITEMS_DICT.items()}
