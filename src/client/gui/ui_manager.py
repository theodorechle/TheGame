import pygame
from ui_element_interface import UIElementInterface
from ui_manager_interface import UIManagerInterface

from json import load, JSONDecodeError
from typing import Any
import os

ELEMENT_HOVERED = pygame.event.custom_type()
ELEMENT_CLICKED = pygame.event.custom_type()
ELEMENT_UNCLICKED = pygame.event.custom_type()
ELEMENT_WHEEL_MOVED = pygame.event.custom_type()

class UIManager(UIManagerInterface):
    def __init__(self, window: pygame.Surface, window_background_image: str|pygame.Surface|None=None) -> None:
        self.window: pygame.Surface = window
        self._elements: list[UIElementInterface] = []
        self._elements_to_display: list[UIElementInterface] = []
        self._refresh_all = False
        self._focused_element: UIElementInterface|None = None
        self._clicked_elements: set[UIElementInterface] = set()
        self._unclicked_elements: set[UIElementInterface] = set()
        self._hovered_elements: set[UIElementInterface] = set()
        self._theme = self.get_theme(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_theme.json'))
        if not self._theme:
            raise FileNotFoundError("Can't find default theme file or file is not valid json")
        self.background_image = None
        if isinstance(window_background_image, str):
            try:
                self.background_image = pygame.image.load(window_background_image)
            except FileNotFoundError:
                pass
        elif isinstance(window_background_image, pygame.Surface):
            self.background_image= window_background_image
        self.scaled_background_image: pygame.Surface|None = None
        self._resize_background_image()

    def _resize_background_image(self) -> None:
        if self.background_image is not None:
            self.scaled_background_image = pygame.transform.scale(self.background_image, self.get_window_size())

    def get_theme(self, path: str) -> dict[str, Any]:
        try:
            with open(path) as f:
                return load(f)
        except (FileNotFoundError, JSONDecodeError):
            print(f"Path '{path}' not found")
            return {}
    
    def _update_elements_themes(self, theme: dict[str,dict[str,Any]]) -> None:
        for element_theme in theme:
            if element_theme in self._theme:
                self._theme[element_theme].update(theme[element_theme])
            else:
                self._theme[element_theme] = theme[element_theme]

    def update_theme(self, path: str|None=None, theme_dict: dict[str, Any]|None=None, erase: bool=False) -> None:
        if erase:
            self._theme.clear()
        changed = False
        if path is not None:
            changed = True
            self._update_elements_themes(self.get_theme(path))
        if theme_dict is not None:
            changed = True
            self._update_elements_themes(theme_dict)
        if changed:
            for element in self._elements:
                element.update_theme(self._theme, erase)
                element.update_element()
            self.ask_refresh()

    def update_element_theme(self, element: UIElementInterface, erase: bool=False) -> None:
        element.update_theme(self._theme, erase)

    def get_window_size(self) -> tuple[int, int]:
        return self.window.get_size()

    def get_window(self) -> pygame.Surface:
        return self.window

    def add_element(self, element: UIElementInterface) -> None:
        self._elements.append(element)
        element.update_theme(self._theme)
        self.ask_refresh()
    
    def remove_element(self, element: UIElementInterface) -> None:
        if element in self._elements:
            self._elements.remove(element)
        if element in self._elements_to_display:
            self._elements_to_display.remove(element)
        if element in self._clicked_elements:
            self._clicked_elements.remove(element)
        if element in self._unclicked_elements:
            self._unclicked_elements.remove(element)
        if element in self._hovered_elements:
            self._hovered_elements.remove(element)
        if self._focused_element == element:
            self._focused_element = None
        self.ask_refresh()

    def delete_all_elements(self) -> None:
        self._elements.clear()
        self._elements_to_display.clear()
        self._clicked_elements.clear()
        self._unclicked_elements.clear()
        self._hovered_elements.clear()
        self.set_focus(None)
        self.ask_refresh()

    def ask_refresh(self, element: UIElementInterface|list[UIElementInterface]|None=None) -> None:
        """
        Ask the UIManager to re-display the window the next time it will be called for an update.
        If an element is given, it will only re-display the element.

        Note: If an element or a list of element is given, it will display it without caring of a size change, 
        so it should be given only if the starting coords and the size are the same as at the last refresh.
        """
        if element is None:
            self._refresh_all = True
            return
        if isinstance(element, UIElementInterface):
            if element in self._elements_to_display: return
            self._elements_to_display.append(element)
        else:
            for e in element:
                if e in self._elements_to_display: continue
                self._elements_to_display.append(e)

    def display(self, clear: bool=True) -> None:
        """
        If clear is set to True, will fill the window with the background color or imag
        """
        if self._refresh_all:
            if clear:
                if self.background_image is not None:
                    self.window.blit(self.scaled_background_image, (0, 0))
                else:
                    self.window.fill(self._theme['window']['background-color'])
            elements = self._elements
        else:
            elements = self._elements_to_display
        for element in elements:
            element.display_element()
        self._refresh_all = False
        self._elements_to_display.clear()
        for element in self._unclicked_elements:
            element.set_unclicked(False)
        self._unclicked_elements.clear()
    
    def get_hovered_element(self) -> list[UIElementInterface]:
        x, y = pygame.mouse.get_pos()
        return [element for element in self._elements if element.is_in_element(x, y)]

    def set_focus(self, element: UIElementInterface|None) -> None:
        if self._focused_element is not None:
            self._focused_element.set_focus(False)
        self._focused_element = element
        if element is not None:
            element.set_focus(True)
    
    def get_focus(self) -> UIElementInterface|None:
        return self._focused_element

    def process_event(self, event: pygame.event.Event) -> None:
        """
        Try to process the given events.
        If the event is not MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP or MOUSEWHEEL,
        if an element have the focus, the event will be sent to the focused element
        """
        if event.type == pygame.MOUSEMOTION:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5): return # wheel
            elements = self.get_hovered_element()
            for element in elements:
                element.set_clicked(True)
                self._clicked_elements.add(element)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (4, 5): return # wheel
            elements = self.get_hovered_element()
            is_focused = False
            for element in self._clicked_elements:
                element.set_clicked(False)
                element.set_unclicked(True)
            self._unclicked_elements = self._unclicked_elements.union(self._clicked_elements)
            self._clicked_elements.clear()
            for element in elements:
                if not is_focused and element.is_focusable():
                    is_focused = True
                    if self.get_focus() != element:
                        self.set_focus(element)
                    break
            if not is_focused:
                self.set_focus(None)
        elif event.type == pygame.MOUSEWHEEL:
            x, y = event.x, event.y
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                x, y = y, x
            elements = self.get_hovered_element()
            for element in elements:
                element.wheel_move = x, y
        elif self._focused_element is not None:
            self._focused_element.process_event(event)


    def update(self) -> bool:
        """
        Set for elements if they are hovered or not.
        Re-display elements who need it.
        Call the update method on all the elements.
        Set unclicked to False for each unclicked elements.
        """

        for element in self._hovered_elements:
            element.set_hovered(False)
        self._hovered_elements.clear()
        elements = self.get_hovered_element()
        for element in elements:
            element.set_hovered(True)
            self._hovered_elements.add(element)
        for element in self._elements:
            element.update()
        return self._refresh_all or len(self._elements_to_display) != 0