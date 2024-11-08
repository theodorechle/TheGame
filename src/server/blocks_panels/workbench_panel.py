from recipes import WORKBENCH_RECIPES, craft
from entities.player_interface import PlayerInterface
from blocks_panels.craft_panel import CraftPanel
from typing import Any

class WorkbenchPanel(CraftPanel):
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface) -> None:
        super().__init__(block_data, player)
    
    def craft(self, craft_name: str) -> bool:
        return craft(craft_name, WORKBENCH_RECIPES, self.player.hot_bar_inventory, self.player.main_inventory)