from recipes import FURNACE_RECIPES, smelt
from entities.player_interface import PlayerInterface
from furnace_inventory import FurnaceInventory
from inventory import Inventory
from blocks_panels.craft_panel import CraftPanel
from typing import Any

class FurnacePanel(CraftPanel):
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface) -> None:
        super().__init__(block_data, player)
        self.temp_player_inventory = Inventory(player.main_inventory.get_nb_cells() + player.hot_bar_inventory.get_nb_cells(), player.main_inventory.cells + player.hot_bar_inventory.cells)
        if 'inventory' not in self.block_data:
            self.block_data['inventory'] = FurnaceInventory(5)
        self.block_inventory = self.block_data['inventory']

    def craft(self, craft_name: str) -> bool:
        return smelt(craft_name, FURNACE_RECIPES, self.block_inventory, self.player.hot_bar_inventory, self.player.main_inventory)