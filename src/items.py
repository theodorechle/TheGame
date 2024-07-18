from load_image import load_image
from blocks import Block

class Item:
    ITEM_SIZE = 20
    PATH = 'src/resources/images/items'
    def __init__(self, name) -> None:
        self.name = name
        self.image = None
        self.stack_size = 99
    
    def load_image(self) -> None:
        self.image = load_image([f'{self.PATH}/{self.name}.png', f'{Block.PATH}/{self.name}.png'], (self.ITEM_SIZE, self.ITEM_SIZE))
    
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

ITEMS: list[Item] = [
    IRON_INGOT,
    STICK,
    STONE_PICKAXE,
    IRON_PICKAXE,
    LAVA_BUCKET,
    EARTH,
    GRASS,
    WOOD,
    SAND,
    STONE,
    COAL,
    IRON,
    PLANK,
    TORCH,
    FURNACE,
    WORKBENCH,
]
