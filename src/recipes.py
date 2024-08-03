import items
from inventory import Inventory

# item name: (need items and qties, crafted items and qties)
WORKBENCH_RECIPES = {
    'stone pickaxe': ([(items.STONE, 2), (items.WOODEN_STICK, 1)], [(items.STONE_PICKAXE, 1)]),
    'iron pickaxe': ([(items.IRON_INGOT, 2), (items.WOODEN_STICK, 1)], [(items.IRON_PICKAXE, 1)]),
    'torch': ([(items.WOODEN_STICK, 1), (items.COAL, 1)], [(items.TORCH, 1)])
}

def craft(craft_name, recipes, inventory: Inventory) -> bool:
    """
    Try to craft the given item and return True if crafted else False
    """
    if craft_name not in recipes: return False
    needed_items, crafted_items = recipes[craft_name]
    for item, qty in needed_items:
        if not inventory.is_present_in_quantity(item, qty): return False
    for item, qty in needed_items:
        inventory.remove_quantity(item, qty)
    for item, qty in crafted_items:
        inventory.add_element(item, qty)
    return True