from gui.ui_manager_interface import UIManagerInterface
from gui.ui_element_interface import UIElementInterface
import pygame

from typing import Any

class UIElement:
    def __init__(self, ui_manager: UIManagerInterface, start_x: int|None=None, start_y: int|None=None, width: int|None=None, height: int|None=None, horizontal_center: bool=False, vertical_center: bool=False, visible: bool=True, parent: UIElementInterface|None=None, theme_elements_name: list[str]=None) -> None:
        """
        Params:
        - ui_manager: the manager where will be send events and who keeps informations like window size
        - start_x: the x of the start of the element, or the center of the element if horizontally centered
        - start_y: the y of the start of the element, or the center of the element if vertically centered
        - width: if not None, set the element width, else set relative size to True for width
        - height: if not None, set the element height, else set relative size to True for height
        - horizontal_center: center the element horizontally in the window
        - vertical_center: center the element vertically in the window
        - visible: Whether the element should be displayed or not
        - theme_elements_name: a list of the themes' names of the subclasses
        """
        if start_x is None and not horizontal_center:
            raise ValueError("'start_x' must be set or 'horizontal_center' have to be set to True")
        if start_y is None and not vertical_center:
            raise ValueError("'start_y' must be set or 'vertical_center' have to be set to True")
        self.theme_elements_name = ['ui-element'] # a list of the class name and all is subclasses to get the themes
        if theme_elements_name is not None:
            self.theme_elements_name.extend(theme_elements_name)
        self._theme = {}
        self._ui_manager = ui_manager
        self._ui_manager.add_element(self)
        self._coords = start_x, start_y
        self._start_coords = self._coords
        self._size = (width, height)
        self._relative_width = width is None
        self._relative_height = height is None
        self._horizontal_center = horizontal_center
        self._vertical_center = vertical_center
        self._visible = visible
        self._parent = parent
        self._hovered = False
        self._clicked = False
        self._unclicked = False
        self.update_element()

    def update_element(self) -> None:
        self.update_size()
        self.update_start_coords()

    def update_theme(self, theme_dict: dict[str, Any], erase=False) -> None:
        """
        If erase is False, only the changed and added values will be set
        """
        if erase:
            self._theme.clear()
        for element_name in self.theme_elements_name:
            if element_name in theme_dict:
                self._theme.update(theme_dict[element_name])

    def update_start_coords(self) -> None:
        x, y = self._coords
        screen_size = self._ui_manager.get_window_size()
        content_size = self.get_size()
        if self._horizontal_center:
            x = screen_size[0] // 2 - content_size[0] // 2 - self.get_theme_value('edges-width')
        if self._vertical_center:
            y = screen_size[1] // 2 - content_size[1] // 2 - self.get_theme_value('edges-width')
        self._start_coords = (x, y)

    def get_start_coords(self) -> tuple[int, int]:
        return self._start_coords
    
    def update_size(self) -> None:
        width, height = self._size
        if self._relative_width or self._relative_height:
            content_width, content_height = self.get_content_size()
        if self._relative_width:
            width = content_width
        if self._relative_height:
            height = content_height
        self._size = (width + 2*self.get_theme_value('edges-width'), height + 2*self.get_theme_value('edges-width'))

    def get_content_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def get_size(self) -> tuple[int, int]:
        return self._size

    def is_in_element(self, x: int, y: int) -> bool:
        return self._start_coords[0] <= x <= self._start_coords[0] + self._size[0] and self._start_coords[1] <= y <= self._start_coords[1] + self._size[1]

    def is_visible(self) -> bool:
        return self._visible
    
    def set_visibility(self, visible: bool) -> None:
        self._visible = visible
        self._ui_manager.ask_refresh()

    def display_element(self) -> bool:
        """
        Check whether the element can be displayed before calling the display method
        """
        if self._visible:
            self.display()
    
    def display(self) -> None:
        """
        Should not be called directly but using display_element method
        """
        raise NotImplementedError
    
    def update(self) -> None:
        """
        Should be called by the subclasses to update the values linked to an event
        (hovered, clicked, ...)
        """
        self._hovered = False
        self._clicked = False
        self._unclicked = False
        
    def get_theme_value(self, variable: str) -> Any|None:
        return self._theme.get(variable)

    def display_edge(self) -> None:
        pygame.draw.rect(
            self._ui_manager.window,
            self.get_theme_value('edges-color'),
            pygame.Rect(
                self._start_coords[0],
                self._start_coords[1],
                self._size[0],
                self._size[1]
            ),
            self.get_theme_value('edges-width'),
            self.get_theme_value('border-radius'),
            self.get_theme_value('border-top-left-radius'),
            self.get_theme_value('border-top-right-radius'),
            self.get_theme_value('border-bottom-left-radius'),
            self.get_theme_value('border-bottom-right-radius')
        )