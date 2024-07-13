import pygame

class Item:
    ITEM_SIZE = 20
    PATH = 'resources/images/items'
    def __init__(self, name) -> None:
        self.name = name
        try:
            image = pygame.image.load(f'{self.PATH}/{self.name}.png')
        except FileNotFoundError:
            image = pygame.image.load(f'{self.PATH}/unknown.png')
        self.image = pygame.transform.scale(image.convert_alpha(),(self.ITEM_SIZE,self.ITEM_SIZE))

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
