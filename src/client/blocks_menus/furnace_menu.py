from pygame import Surface
from gui import elements
from gui.ui_element import UIElement
from recipes import FURNACE_RECIPES, smelt
from player_interface import PlayerInterface
from furnace_inventory import FurnaceInventory
from inventory import Inventory
from blocks_menus.block_menu import BlockMenu, BLOCKS_MENUS_THEMES_PATH
from client.module_infos import RESOURCES_PATH
import os
from typing import Any

class FurnaceMenu(BlockMenu):
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface, window: Surface) -> None:
        super().__init__(block_data, player, window)
        self.temp_player_inventory = Inventory(player.main_inventory._nb_cells + player.hot_bar_inventory._nb_cells, self._ui_manager, player.main_inventory.cells + player.hot_bar_inventory.cells)
        self.temp_player_inventory.toggle_inventory()
        self._ui_manager.update_theme(os.path.join(BLOCKS_MENUS_THEMES_PATH, 'furnace_menu_theme.json'))
        self._ui_manager.update_theme(os.path.join(RESOURCES_PATH, 'gui_themes', 'inventory.json'))
        self.crafts_list = elements.ItemList(self._ui_manager, x='5%', anchor='left', height='80%', width='30%', items_classes_names=['craft-list-childs'], on_select_item_function=self.select_craft)
        self._elements.append(self.crafts_list)
        self.needed_items = elements.ItemList(self._ui_manager, anchor='left', x='40%', width='15%', height='50%', items_classes_names=['item-lists-childs'])
        self._elements.append(self.needed_items)
        self.needed_quantities = elements.ItemList(self._ui_manager, anchor='left', x='55%', width='5%', height='50%', items_classes_names=['item-lists-childs'])
        self._elements.append(self.needed_quantities)
        self._elements.append(elements.Label(self._ui_manager, '/', anchor='left', x='60%', width='2%', classes_names=['craft-actual-on-needed-label', 'craft-indicator-label']))
        self.actual_quantities = elements.ItemList(self._ui_manager, anchor='left', x='62%', width='5%', height='50%', items_classes_names=['item-lists-childs'])
        self._elements.append(self.actual_quantities)
        self._elements.append(elements.Label(self._ui_manager, '=', anchor='left', x='67%', width='3%', classes_names=['craft-give-label', 'craft-indicator-label']))
        self.crafted_items = elements.ItemList(self._ui_manager, anchor='left', x='70%', width='15%', height='50%', items_classes_names=['item-lists-childs'])
        self._elements.append(self.crafted_items)
        self.crafted_quantities = elements.ItemList(self._ui_manager, anchor='left', x='85%', width='5%', height='50%', items_classes_names=['item-lists-childs'])
        self._elements.append(self.crafted_quantities)
        self._elements.append(elements.TextButton(self._ui_manager, 'Craft', self.craft_item, anchor='center', x='45%'))
        if 'inventory' not in self.block_data:
            self.block_data['inventory'] = FurnaceInventory(5, self._ui_manager)
        self.block_inventory = self.block_data['inventory']
        self.add_crafts()
    
    def add_crafts(self) -> None:
        self.crafts_list.add_elements(list(FURNACE_RECIPES.keys()))
    
    def craft_item(self, _: UIElement) -> None:
        selected_craft = self.crafts_list.child_selected
        if selected_craft is None: return
        if smelt(selected_craft.get_text(), FURNACE_RECIPES, self.block_inventory, self.player.hot_bar_inventory, self.player.main_inventory):
            self.need_update = True
            self.select_craft(self.crafts_list.child_selected)
    
    def select_craft(self, button: elements.TextButton) -> None:
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
