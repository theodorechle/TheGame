from abc import ABCMeta, abstractmethod

class EntityInterface(metaclass=ABCMeta):
    @abstractmethod
    def scale_image(self) -> None:
        pass

    @abstractmethod
    def set_player_edges_pos(self) -> None:
        pass

    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def update(self, delta_t: float) -> bool:
        pass
