from abc import ABCMeta, abstractmethod
from entities.entity_interface import EntityInterface
from inventory_interface import InventoryInterface
from typing import Any

class PlayerInterface(EntityInterface, metaclass=ABCMeta):
    def __init__(self) -> None:
        self.main_inventory: InventoryInterface
        self.hot_bar_inventory: InventoryInterface
    
    @abstractmethod
    def display_hud(self) -> None:
        pass

    @abstractmethod
    def _display_infos(self) -> None:
        pass

    @abstractmethod
    async def update(self, update_dict: dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def place_block(self, pos: tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def remove_block(self, pos: tuple[int, int]) -> bool:
        pass