Block = int

NOTHING = -1
AIR = 0
EARTH = 1
GRASS = 2
WOOD = 3
LEAVES = 4
SAND = 5
STONE = 6
COAL = 7
IRON = 8
PLANK = 9
LAVA = 10
NIGHT = 11
TORCH = 12
FURNACE = 13
WORKBENCH = 14
WATER = 15
SNOW = 16
# new blocks must be added to the end in order to not break existing saves

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
    WORKBENCH,
    # FURNACE: FurnaceMenu
}