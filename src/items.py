from load_image import load_image

class Item:
    ITEM_SIZE = 20
    PATH = 'src/resources/images/items'
    def __init__(self, name) -> None:
        self.name = name
        self.image = None
    
    def load_image(self) -> None:
        self.image = load_image(f'{self.PATH}/{self.name}.png', (self.ITEM_SIZE, self.ITEM_SIZE))

ITEMS = [
    Item('coal'),
    Item('iron_ingot'),
    Item('iron_pickaxe'),
    Item('iron'),
    Item('lava_bucket'),
    Item('stick'),
    Item('stone_pickaxe'),
    Item('torch')
]
