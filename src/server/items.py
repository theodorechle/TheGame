class Item:
    def __init__(self, stack_size: int=99) -> None:
        self.stack_size = stack_size

NOTHING = None
IRON_INGOT = 0
WOODEN_STICK = 1
STONE_PICKAXE = 2
IRON_PICKAXE = 3
LAVA_BUCKET = 4
EARTH = 5
GRASS = 6
WOOD = 7
SAND = 8
STONE = 9
COAL = 10
IRON_NUGGET = 11
PLANK = 12
TORCH = 13
FURNACE = 14
WORKBENCH = 15
SNOW = 16
# new items must be added to the end in order to not break the existing saves
