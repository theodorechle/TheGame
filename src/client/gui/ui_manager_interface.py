from ui_element_interface import UIElementInterface
from pygame.event import Event
from abc import abstractmethod, ABCMeta

from pygame import Surface

from typing import Any

class UIManagerInterface(metaclass=ABCMeta):
    @abstractmethod
    def _resize_background_image(self) -> None:
        pass

    @abstractmethod
    def get_theme(self, path: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def _update_elements_themes(self, theme: dict[str,dict[str,Any]]) -> None:
        pass

    @abstractmethod
    def update_theme(self, path: str|None=None, theme_dict: dict[str, Any]|None=None, erase: bool=False) -> None:
        pass

    @abstractmethod
    def update_element_theme(self, element: UIElementInterface, erase: bool=False) -> None:
        pass

    @abstractmethod
    def get_window_size(self) -> tuple[int, int]:
        pass
    
    @abstractmethod
    def get_window(self) -> Surface:
        pass

    @abstractmethod
    def add_element(self, element: UIElementInterface) -> None:
        pass
    
    @abstractmethod
    def remove_element(self, element: UIElementInterface) -> None:
        pass

    @abstractmethod
    def delete_all_elements(self) -> None:
        pass

    @abstractmethod
    def ask_refresh(self, element: UIElementInterface|list[UIElementInterface]|None=None) -> None:
        """
        Ask the UIManager to re-display the window the next time it will be called for an update.
        If an element is given, it will only re-display the element.

        Note: If an element is given, it will display it without caring of a size change, 
        so it should be given only if the starting coords and the size are the same as at the last refresh.
        """
    
    @abstractmethod
    def display(self) -> None:
        pass
    
    @abstractmethod
    def get_hovered_element(self) -> list[UIElementInterface]:
        pass

    @abstractmethod
    def set_focus(self, element: UIElementInterface|None) -> None:
        pass

    @abstractmethod
    def get_focus(self) -> UIElementInterface|None:
        pass

    @abstractmethod
    def process_event(self, event: Event) -> None:
        """
        Try to process the given events.
        If the event is not MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP or MOUSEWHEEL,
        if an element have the focus, the event will be sent to the focused element
        """

    @abstractmethod
    def update(self) -> None:
        """Refresh the window if needed and creates events (click, hover)"""
