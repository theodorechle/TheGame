from typing import Any
from pygame import Surface
from blocks_panels.block_panel import BlockPanel
from entities.player_interface import PlayerInterface
from abc import abstractmethod, ABCMeta

class CraftPanel(BlockPanel, metaclass=ABCMeta):
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface) -> None:
        super().__init__(block_data, player)
    
    @abstractmethod
    def craft(self, craft_name: str) -> bool:
        pass