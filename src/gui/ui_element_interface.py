from abc import abstractmethod, ABCMeta
from typing import Any

class UIElementInterface(metaclass=ABCMeta):
    @abstractmethod
    def set_default_theme(self) -> None:
        pass

    @abstractmethod
    def update_start_coords(self) -> None:
        pass

    @abstractmethod
    def get_start_coords(self) -> tuple[int, int]:
        pass
    
    @abstractmethod
    def update_size(self) -> None:
        ...

    @abstractmethod
    def get_content_size(self) -> tuple[int, int]:
        pass

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        pass

    @abstractmethod
    def is_in_element(self, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def is_visible(self) -> bool:
        pass
    
    @abstractmethod
    def set_visibility(self, visible: bool) -> None:
        pass

    @abstractmethod
    def display_element(self) -> bool:
        """Check whether the element can be displayed before calling the display method"""
    
    @abstractmethod
    def display(self) -> None:
        """Should not be called directly but using display_element method"""
    
    @abstractmethod
    def update(self) -> None:
        pass
    
    @abstractmethod
    def get_theme_value(self, variable: str) -> Any|None:
        pass

    @abstractmethod
    def display_edge(self) -> None:
        pass
