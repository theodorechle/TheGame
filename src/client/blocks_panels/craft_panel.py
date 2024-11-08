from typing import Any
from pygame import Surface
from blocks_panels.block_panel import BlockPanel
from entities.player_interface import PlayerInterface
from gui.ui_element import UIElement
from abc import abstractmethod, ABCMeta

class CraftPanel(BlockPanel, metaclass=ABCMeta):
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface, window: Surface, *ui_manager_parameters: list[Any]) -> None:
        super().__init__(block_data, player, window, *ui_manager_parameters)
        self._ask_craft = False
    
    @abstractmethod
    def _get_selected_craft(self) -> str|None:
        pass

    def _craft(self, _: UIElement) -> None:
        self._ask_craft = True

    def get_item_to_craft(self) -> str|None:
        return self._get_selected_craft() if self._ask_craft else None

    @abstractmethod
    def update_after_craft(self) -> None:
        pass

    def update(self) -> bool:
        self._ask_craft = False
        return super().update()