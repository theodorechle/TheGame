from abc import abstractmethod, ABCMeta
from typing import Any

from pygame.event import Event
from pygame import Rect

class UIElementInterface(metaclass=ABCMeta):
    @abstractmethod
    def _resize_background_image(self) -> None:
        pass

    @abstractmethod
    def update_element(self) -> None:
        pass

    @abstractmethod
    def update_theme(self, theme_dict: dict[str, Any], erase: bool=False) -> None:
        """If erase is False, only the changed and added values will be set"""

    @abstractmethod
    def get_start_coords(self) -> tuple[int, int]:
        pass
    
    @abstractmethod
    def get_surface_rect(self) -> Rect:
        pass

    @abstractmethod
    def update_start_coords(self) -> None:
        pass

    @abstractmethod
    def get_relative_width(self, width: str) -> int:
        pass

    def get_relative_height(self, height: str) -> int:
        pass

    @abstractmethod
    def update_size(self) -> None:
        pass

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
    def get_visibility(self) -> bool:
        pass
    
    @abstractmethod
    def set_visibility(self, visible: bool) -> None:
        pass

    @abstractmethod
    def toggle_visibility(self) -> bool:
        """Returns True if visible else False"""
    
    @abstractmethod
    def set_focus(self, focus: bool) -> bool:
        pass

    @abstractmethod
    def set_selected(self, selected: bool) -> None:
        pass

    @abstractmethod
    def set_clicked(self, clicked: bool) -> None:
        pass

    @abstractmethod
    def set_unclicked(self, unclicked: bool) -> None:
        pass

    @abstractmethod
    def set_hovered(self, hovered: bool) -> None:
        pass

    @abstractmethod
    def is_focusable(self) -> bool:
        pass

    @abstractmethod
    def display_element(self) -> None:
        """Check whether the element can be displayed before calling the display method"""

    @abstractmethod
    def _display(self) -> None:
        """Should not be called directly but using display_element method"""
    
    @abstractmethod
    def update(self) -> None:
        """
        Should be called by the subclasses to update the values linked to an event
        (hovered, clicked, ...)
        """
    
    @abstractmethod
    def get_theme_value(self, variable: str) -> Any|None:
        pass

    @abstractmethod
    def display_borders(self) -> None:
        pass

    @abstractmethod
    def process_event(self, event: Event) -> None:
        """
        If the element have the focus and the event can't be processed by the ui manager,
        the element will receive the events in order to process them.
        """
    
    @abstractmethod
    def get_parent(self) -> 'UIElementInterface|None':
        pass