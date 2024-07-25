import pygame
from gui.ui_element import UIElement

from json import load, JSONDecodeError
from typing import Any

ELEMENT_HOVERED = pygame.event.custom_type()
ELEMENT_CLICKED = pygame.event.custom_type()
ELEMENT_UNCLICKED = pygame.event.custom_type()

class UIManager:
    def __init__(self, window: pygame.Surface) -> None:
        self.window = window
        self._elements: list[UIElement] = []
        self._elements_to_display: list[UIElement] = []
        self._refresh_all = False
        self._theme = self.get_theme('src/gui/default_theme.json')
        if not self._theme:
            raise FileNotFoundError("Can't find default theme file")

    def get_theme(self, path: str) -> dict[str, Any]:
        try:
            with open(path) as f:
                return load(f)
        except (FileNotFoundError, JSONDecodeError):
            return {}
    
    def update_theme(self, path: str=None, theme_dict: dict[str, Any]|None=None, erase: bool=False) -> None:
        if erase:
            self._theme.clear()
        if path is not None:
            self._theme.update(self.get_theme(path))
        if theme_dict is not None:
            self._theme.update(theme_dict)
        for element in self._elements:
            element.update_theme(self._theme, erase)

    def get_window_size(self) -> tuple[int, int]:
        return self.window.get_size()
    
    def add_element(self, element: UIElement) -> None:
        self._elements.append(element)
        element.update_theme(self._theme)
        self.ask_refresh()
    
    def remove_element(self, element: UIElement) -> None:
        try:
            self._elements.remove(element)
            self.ask_refresh()
        except ValueError:
            pass

    def clear_elements_list(self) -> None:
        self._elements.clear()
        self._elements_to_display.clear()

    def ask_refresh(self, element: UIElement|None=None) -> None:
        """
        Ask the UIManager to re-display the window the next time it will be called for an update.
        If an element is given, it will only re-display the element.
        Note: If an element is given, it will display it without caring of a size change, 
        so it should be given only if the starting coords and the size are the same as at the last refresh.
        """
        if element is not None:
            self._elements_to_display.append()
        else:
            self._refresh_all = True

    def display(self) -> None:
        if self._refresh_all:
            self.window.fill("#000000")
            elements = self._elements
        else:
            elements = self._elements_to_display
        for element in elements:
            element.display_element()
        self._refresh_all = False
        self._elements_to_display.clear()
    
    def get_hovered_element(self) -> UIElement|None:
        x, y = pygame.mouse.get_pos()
        for element in reversed(self._elements): # run backwards as last displayed elements are one the top of the elements
            if element.is_in_element(x, y):
                return element

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            element = self.get_hovered_element()
            while element is not None:
                element._hovered = True
                pygame.event.post(pygame.event.Event(ELEMENT_HOVERED, dict={'element': element}))
                element = element._parent
        elif event.type == pygame.MOUSEBUTTONDOWN:
            element = self.get_hovered_element()
            while element is not None:
                element._clicked = True
                pygame.event.post(pygame.event.Event(ELEMENT_CLICKED, dict={'element': element}))
                element = element._parent
        elif event.type == pygame.MOUSEBUTTONUP:
            element = self.get_hovered_element()
            while element is not None:
                element._unclicked = True
                pygame.event.post(pygame.event.Event(ELEMENT_UNCLICKED, dict={'element': element}))
                element = element._parent            

    def update(self) -> None:
        """
        Refresh the window if needed and creates events (click, hover)
        """
        self.display()
        for element in self._elements:
            element.update()
