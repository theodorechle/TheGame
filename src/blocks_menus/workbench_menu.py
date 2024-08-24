from pygame import Surface
from gui import elements
from gui.ui_element import UIElement
from recipes import WORKBENCH_RECIPES, craft
from inventory import Inventory
from blocks_menus.block_menu import BlockMenu, BLOCKS_MENUS_THEMES_PATH
import os
from typing import Any

class WorkbenchMenu(BlockMenu):
    def __init__(self, block_data: dict[str, Any], player_inventory: Inventory, window: Surface) -> None:
        super().__init__(block_data, player_inventory, window)
        self._ui_manager.update_theme(os.path.join(BLOCKS_MENUS_THEMES_PATH, 'workbench_menu_theme.json'))
        self.crafts_list = elements.ItemList(self._ui_manager, x='5%', anchor='left', height='80%', width='30%', classes_names=['craft-list'], on_select_item_function=self.select_craft)
        self._elements.append(self.crafts_list)
        self.needed_items = elements.ItemList(self._ui_manager, anchor='left', x='40%', width='15%', height='50%')
        self._elements.append(self.needed_items)
        self.needed_quantities = elements.ItemList(self._ui_manager, anchor='left', x='55%', width='5%', height='50%')
        self._elements.append(self.needed_quantities)
        self._elements.append(elements.Label(self._ui_manager, '/', anchor='left', x='60%', width='2%', classes_names=['craft-actual-on-needed-label', 'craft-indicator-label']))
        self.actual_quantities = elements.ItemList(self._ui_manager, anchor='left', x='62%', width='5%', height='50%')
        self._elements.append(self.actual_quantities)
        self._elements.append(elements.Label(self._ui_manager, '=', anchor='left', x='67%', width='3%', classes_names=['craft-give-label', 'craft-indicator-label']))
        self.crafted_items = elements.ItemList(self._ui_manager, anchor='left', x='70%', width='15%', height='50%')
        self._elements.append(self.crafted_items)
        self.crafted_quantities = elements.ItemList(self._ui_manager, anchor='left', x='85%', width='5%', height='50%')
        self._elements.append(self.crafted_quantities)
        self._elements.append(elements.TextButton(self._ui_manager, 'Craft', self.craft_item, anchor='center', x='45%'))
        self.add_crafts()
    
    def add_crafts(self) -> None:
        self.crafts_list.add_elements(list(WORKBENCH_RECIPES.keys()))
    
    def craft_item(self, _: UIElement) -> None:
        selected_craft = self.crafts_list.child_selected
        if selected_craft is None: return
        if craft(selected_craft.get_text(), WORKBENCH_RECIPES, self.player_inventory):
            self.need_update = True
            self.select_craft(self.crafts_list.child_selected)
    
    def select_craft(self, button: elements.TextButton) -> None:
        craft_name = button.get_text()
        if craft_name not in WORKBENCH_RECIPES: return
        needed_items, crafted_items = WORKBENCH_RECIPES[craft_name]
        self.needed_items.remove_all_elements()
        self.needed_quantities.remove_all_elements()
        self.actual_quantities.remove_all_elements()
        self.crafted_items.remove_all_elements()
        self.crafted_quantities.remove_all_elements()
        for item in needed_items:
            self.needed_items.add_element(item[0].name)
            self.needed_quantities.add_element(str(item[1]))
            qty = self.player_inventory.get_element_quantity(item[0])
            self.actual_quantities.add_element(str(qty))
            if qty < item[1]:
                self.actual_quantities._elements[-1].label._theme['text-color'] = "#ff0000"
        for item in crafted_items:
            self.crafted_items.add_element(item[0].name)
            self.crafted_quantities.add_element(str(item[1]))
        