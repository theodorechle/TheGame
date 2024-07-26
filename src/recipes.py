import blocks
import items
from random import randint

_BLOCKS_TO_ITEMS: dict[blocks.Block, list[items.Item, int|tuple]] = {
    blocks.EARTH: [items.EARTH, 1],
    blocks.GRASS: [items.GRASS, 1],
    blocks.WOOD: [items.WOOD, 1],
    blocks.LEAVES: [items.STICK, (1, 2)],
    blocks.SAND: [items.SAND, 1],
    blocks.STONE: [items.STONE, 1],
    blocks.COAL: [items.COAL, (1, 3)],
    blocks.IRON: [items.IRON, (1, 2)],
    blocks.PLANK: [items.PLANK, 1],
    blocks.TORCH: [items.TORCH, 1],
    blocks.FURNACE: [items.FURNACE, 1],
    blocks.WORKBENCH: [items.WORKBENCH, 1],
    blocks.SNOW: [items.SNOW, 1]
}

_ITEM_TO_BLOCK: dict[items.Item, blocks.Block] = {
    items.EARTH: blocks.EARTH,
    items.GRASS: blocks.GRASS,
    items.WOOD: blocks.WOOD,
    items.SAND: blocks.SAND,
    items.STONE: blocks.STONE,
    items.PLANK: blocks.PLANK,
    items.TORCH: blocks.TORCH,
    items.FURNACE: blocks.FURNACE,
    items.WORKBENCH: blocks.WORKBENCH,
    items.SNOW: blocks.SNOW
}

def convert_block_to_items(block: blocks.Block, quantity: int) -> dict[items.Item, int]:
    """
    Returns a list of items with their quantity
    """
    if block not in _BLOCKS_TO_ITEMS: return {}
    final_items = {}
    recipe = _BLOCKS_TO_ITEMS[block]
    for index in range(0, len(recipe), 2):
        final_items[recipe[index]] = 0
    
    for _ in range(quantity):
        for index in range(0, len(recipe), 2):
            itm = recipe[index]
            qty = recipe[index + 1]
            if isinstance(qty, tuple):
                qty = randint(qty[0], qty[1])
            final_items[itm] += qty
    return final_items

def convert_item_to_block(item: items.Item) -> blocks.Block:
    return _ITEM_TO_BLOCK.get(item, None)