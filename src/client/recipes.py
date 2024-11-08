import items
from inventory import Inventory
from furnace_inventory import FurnaceInventory

# item name: (needed items and qties, crafted items and qties)
WORKBENCH_RECIPES = {
    'stone pickaxe': ([(items.STONE, 2), (items.WOODEN_STICK, 1)], [(items.STONE_PICKAXE, 1)]),
    'iron pickaxe': ([(items.IRON_INGOT, 2), (items.WOODEN_STICK, 1)], [(items.IRON_PICKAXE, 1)]),
    'torch': ([(items.WOODEN_STICK, 1), (items.COAL, 1)], [(items.TORCH, 1)]),
    'planks': ([(items.WOOD, 1)], [(items.PLANK, 2)])
}

# item name: (needed items and qties, crafted items and qties), qty of energy needed
FURNACE_RECIPES = {
    'iron ingot': ([(items.IRON_NUGGET, 2)], [(items.IRON_INGOT, 1)], 5)
}

# comburant name: energy produced
COMBURANTS = {
    items.COAL: 15,
    items.WOOD: 10,
    items.WOODEN_STICK: 3
}