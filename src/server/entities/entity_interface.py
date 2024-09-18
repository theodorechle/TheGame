from abc import ABCMeta, abstractmethod

class EntityInterface(metaclass=ABCMeta):
    @abstractmethod
    def set_player_edges_pos(self) -> None:
        pass

    @abstractmethod
    def update(self, delta_t: float) -> bool:
        pass
