from abc import ABCMeta, abstractmethod
from entities.entity_interface import EntityInterface
from inventory_interface import InventoryInterface

class PlayerInterface(EntityInterface, metaclass=ABCMeta):
    def __init__(self) -> None:
        self.main_inventory: InventoryInterface = None
        self.hot_bar_inventory: InventoryInterface = None
    
    @abstractmethod
    def display_hud(self) -> None:
        pass

    @abstractmethod
    def _display_infos(self) -> None:
        pass

    @abstractmethod
    def update(self, delta_t: float) -> bool:
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