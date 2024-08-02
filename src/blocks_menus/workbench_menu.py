from pygame import Surface
from gui import elements
from gui.ui_element import UIElement
from recipes import WORKBENCH_RECIPES, craft

from blocks_menus.block_menu import BlockMenu, BLOCKS_MENUS_THEMES_PATH
import os

class WorkbenchMenu(BlockMenu):
    def __init__(self, window: Surface, player_inventory) -> None:
        super().__init__(window)
        self._ui_manager.update_theme(os.path.join(BLOCKS_MENUS_THEMES_PATH, 'workbench_menu_theme.json'))
        self.player_inventory = player_inventory
        self.crafts_list = elements.ItemList(self._ui_manager, x='5%', anchor='left', height='80%', width='50%', childs_classes_names=['item-list-childs'])
        self._elements.append(self.crafts_list)
        self._elements.append(elements.Button(self._ui_manager, 'Craft', self.craft_item, anchor='right', x='-25%'))
        self.add_crafts()
    
    def add_crafts(self) -> None:
        self.crafts_list.add_elements(list(WORKBENCH_RECIPES.keys()))
    
    def craft_item(self, _: UIElement) -> None:
        selected_craft = self.crafts_list.child_selected
        if selected_craft is None: return
        if craft(selected_craft.get_text(), WORKBENCH_RECIPES, self.player_inventory):
            self.need_update = True