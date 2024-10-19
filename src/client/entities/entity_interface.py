from abc import ABCMeta, abstractmethod
from typing import Any

class EntityInterface(metaclass=ABCMeta):
    @abstractmethod
    def load_image(self) -> None:
        pass

    @abstractmethod
    def set_player_edges_pos(self) -> None:
        pass

    @abstractmethod
    def display(self, rel_x: int, rel_y: int) -> None:
        pass

    @abstractmethod
    def update(self, update_dict: dict[str, Any]) -> None:
        pass
