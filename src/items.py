from load_image import load_image

class Item:
    ITEM_SIZE = 20
    PATH = 'src/resources/images/items'
    def __init__(self, name) -> None:
        self.name = name
        self.image = None
    
    def load_image(self) -> None:
        self.image = load_image(f'{self.PATH}/{self.name}.png', (self.ITEM_SIZE, self.ITEM_SIZE))

COAL = Item('coal')
IRON = Item('iron')
IRON_INGOT = Item('iron_ingot')
STICK = Item('stick')
STONE_PICKAXE = Item('stone_pickaxe')
IRON_PICKAXE = Item('iron_pickaxe')
LAVA_BUCKET = Item('lava_bucket')
TORCH = Item('torch')

ITEMS: list[Item] = [
    COAL,
    IRON,
    IRON_INGOT,
    STICK,
    STONE_PICKAXE,
    IRON_PICKAXE,
    LAVA_BUCKET,
    TORCH
]
