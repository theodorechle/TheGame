from recipes import WORKBENCH_RECIPES, craft
from entities.player_interface import PlayerInterface
from blocks_interfaces.block_interface import BlockInterface
from typing import Any

class WorkbenchInterface(BlockInterface):
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface) -> None:
        super().__init__(block_data, player)
    
    def craft_item(self, craft_name: str) -> None:
        return craft(craft_name, WORKBENCH_RECIPES, self.player.hot_bar_inventory, self.player.main_inventory)