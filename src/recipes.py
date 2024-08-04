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

def get_energy_quantity(inventory: Inventory) -> int:
    energy = 0
    for cell in inventory.cells:
        if cell[0] in COMBURANTS:
            energy += COMBURANTS[cell[0]] * cell[1]
    return energy

def remove_energy(inventory: FurnaceInventory, energy_qty: int) -> None:
    """
    Remove the given quantity of energy from the inventory by removing comburant items.
    """
    if inventory.burning_item is not None:
        energy = inventory.burning_item[1]
        removed_energy = min(energy, energy_qty)
        if removed_energy < energy:
            inventory.set_burning_item(inventory.burning_item[0], energy - removed_energy)
            return
        energy_qty -= removed_energy

    for index, cell in enumerate(inventory.cells):
        if energy_qty == 0: return
        if cell[0] in COMBURANTS:
            energy = COMBURANTS[cell[0]] * cell[1]
            removed_energy = min(energy, removed_energy)
            if removed_energy < energy:
                inventory.cells[index] = cell[0], (energy - removed_energy) // COMBURANTS[cell[0]]
                inventory.set_burning_item(cell[0], (energy - removed_energy) % COMBURANTS[cell[0]])
                return
            inventory.cells[index] = (items.NOTHING, 0)
            energy_qty -= removed_energy

def smelt(craft_name, recipes, inventory: Inventory, furnace_inventory: FurnaceInventory) -> bool:
    if craft_name not in recipes: return False
    needed_items, crafted_items, energy_needed = recipes[craft_name]
    available_energy = get_energy_quantity(furnace_inventory)
    if available_energy < energy_needed: return False
    for item, qty in needed_items:
        if not inventory.is_present_in_quantity(item, qty): return False
    for item, qty in needed_items:
        inventory.remove_quantity(item, qty)
    remove_energy(furnace_inventory, energy_needed)
    for item, qty in crafted_items:
        inventory.add_element(item, qty)
    return True