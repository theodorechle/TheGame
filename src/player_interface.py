from abc import ABCMeta, abstractmethod
from entity_interface import EntityInterface

class PlayerInterface(EntityInterface, metaclass=ABCMeta):
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