from load_image import load_image
from blocks import BLOCKS_IMAGES_PATH
from module_infos import RESOURCES_PATH

ITEMS_IMAGES_PATH = f'{RESOURCES_PATH}/images/items'
class Item:
    ITEM_SIZE = 40
    def __init__(self, path: str) -> None:
        self.path = path
        self.name = path.replace('_', ' ')
        self.image = load_image([f'{ITEMS_IMAGES_PATH}/{self.path}.png', f'{BLOCKS_IMAGES_PATH}/{self.path}.png'], None)
    
    def __repr__(self) -> str:
        return self.name

NOTHING = None
IRON_INGOT = Item('iron_ingot')
STONE_PICKAXE = Item('stone_pickaxe')
IRON_PICKAXE = Item('iron_pickaxe')
LAVA_BUCKET = Item('lava_bucket')
EARTH = Item('earth')
GRASS = Item('grass')
WOOD = Item('wood')
SAND = Item('sand')
STONE = Item('stone')
COAL = Item('coal')
IRON_NUGGET = Item('iron_nugget')
PLANK = Item('plank')
TORCH = Item('torch')
FURNACE = Item('furnace')
WORKBENCH = Item('workbench')
SNOW = Item('snow')
WOODEN_STICK = Item('wooden_stick')

# new items must be added to the end in order to not break the existing saves
ITEMS_DICT: dict[Item, int] = {
    NOTHING: -1,
    IRON_INGOT: 0,
    WOODEN_STICK: 1,
    STONE_PICKAXE: 2,
    IRON_PICKAXE: 3,
    LAVA_BUCKET: 4,
    EARTH: 5,
    GRASS: 6,
    WOOD: 7,
    SAND: 8,
    STONE: 9,
    COAL: 10,
    IRON_NUGGET: 11,
    PLANK: 12,
    TORCH: 13,
    FURNACE: 14,
    WORKBENCH: 15,
    SNOW: 16,
}

REVERSED_ITEMS_DICT: dict[int, Item] = {v: k for k, v in ITEMS_DICT.items()}
