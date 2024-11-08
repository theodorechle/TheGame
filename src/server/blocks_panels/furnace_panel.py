# from recipes import FURNACE_RECIPES, smelt
from entities.player_interface import PlayerInterface
# from furnace_inventory import FurnaceInventory
from inventory import Inventory
from blocks_panels.craft_panel import CraftPanel
from typing import Any

class FurnacePanel(CraftPanel):
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface) -> None:
        super().__init__(block_data, player)
        self.temp_player_inventory = Inventory(player.main_inventory.get_nb_cells() + player.hot_bar_inventory.get_nb_cells(), self._ui_manager, player.main_inventory.cells + player.hot_bar_inventory.cells)
        self.temp_player_inventory.toggle_inventory()
        if 'inventory' not in self.block_data:
            self.block_data['inventory'] = FurnaceInventory(5, self._ui_manager)
        self.block_inventory = self.block_data['inventory']
        self.add_crafts()
    
    def add_crafts(self) -> None:
        self.crafts_list.add_elements(list(FURNACE_RECIPES.keys()))
    
    def craft(self) -> None:
        selected_craft = self.crafts_list.child_selected
        if selected_craft is None: return
        if smelt(selected_craft.get_text(), FURNACE_RECIPES, self.block_inventory, self.player.hot_bar_inventory, self.player.main_inventory):
            self.need_update = True
            self.select_craft(self.crafts_list.child_selected)
    
    def select_craft(self) -> None:
        craft_name = button.get_text()
        if craft_name not in FURNACE_RECIPES: return
        needed_items, crafted_items, need_energy = FURNACE_RECIPES[craft_name]
        self.needed_items.remove_all_elements()
        self.needed_quantities.remove_all_elements()
        self.actual_quantities.remove_all_elements()
        self.crafted_items.remove_all_elements()
        self.crafted_quantities.remove_all_elements()
        inventories = self.player.hot_bar_inventory, self.player.main_inventory
        for item in needed_items:
            self.needed_items.add_element(item[0].name)
            self.needed_quantities.add_element(str(item[1]))
            qty = sum(inventory.get_element_quantity(item[0]) for inventory in inventories)
            self.actual_quantities.add_element(str(qty))
            if qty < item[1]:
                self.actual_quantities._elements[-1].label._theme['text-color'] = "#ff0000"
        for item in crafted_items:
            self.crafted_items.add_element(item[0].name)
            self.crafted_quantities.add_element(str(item[1]))
