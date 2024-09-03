from abc import ABCMeta, abstractmethod
from entity_interface import EntityInterface
from inventory_interface import InventoryInterface

class PlayerInterface(EntityInterface, metaclass=ABCMeta):
    def __init__(self) -> None:
        self.main_inventory: InventoryInterface = None
        self.hot_bar_inventory: InventoryInterface = None
    
    @abstractmethod
    def update(self, delta_t: float) -> bool:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def _get_relative_pos(self, x: int, y: int) -> tuple[int, int]:
        pass

    @abstractmethod
    def _is_interactable(self, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def _is_surrounded_by_block(self, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def place_block(self, pos: tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def remove_block(self, pos: tuple[int, int]) -> bool:
        pass