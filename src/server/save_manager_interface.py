from abc import ABCMeta, abstractmethod
from map_chunk import Chunk
from entities.player_interface import PlayerInterface

class SaveManagerInterface(metaclass=ABCMeta):
    @abstractmethod
    def init_repository(self) -> None:
        pass
    
    @abstractmethod
    def load_chunk(self, id: int) -> Chunk|None:
        pass

    @abstractmethod
    def save_chunk(self, chunk: Chunk|None) -> None:
        pass

    @abstractmethod
    def load_players(self) -> list[PlayerInterface]|None:
        pass

    @abstractmethod
    def save_players(self, players: list[PlayerInterface]) -> None:
        pass