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
        self.theme = {}
        self.ui_manager = ui_manager
        self.ui_manager.add_element(self)
        self.coords = start_x, start_y
        self.start_coords = self.coords
        self.size = (width, height)
        self.relative_width = width is None
        self.relative_height = height is None
        self.horizontal_center = horizontal_center
        self.vertical_center = vertical_center
        self.visible = visible
        self.parent = parent
        self.hovered = False
        self.clicked = False
        self.unclicked = False
        self.update_element()

    def update_element(self) -> None:
        self.update_size()
        self.update_start_coords()

    def update_theme(self, theme_dict: dict[str, Any], erase=False) -> None:
        """
        If erase is False, only the changed and added values will be set
        """
        if erase:
            self.theme.clear()
        for element_name in self.theme_elements_name:
            if element_name in theme_dict:
                self.theme.update(theme_dict[element_name])

    def update_start_coords(self) -> None:
        x, y = self.coords
        screen_size = self.ui_manager.get_window_size()
        content_size = self.get_size()
        if self.horizontal_center:
            x = screen_size[0] // 2 - content_size[0] // 2 - self.get_theme_value('edges-width')
        if self.vertical_center:
            y = screen_size[1] // 2 - content_size[1] // 2 - self.get_theme_value('edges-width')
        self.start_coords = (x, y)

    def get_start_coords(self) -> tuple[int, int]:
        return self.start_coords
    
    def update_size(self) -> None:
        width, height = self.size
        if self.relative_width or self.relative_height:
            content_width, content_height = self.get_content_size()
        if self.relative_width:
            width = content_width
        if self.relative_height:
            height = content_height
        self.size = (width + 2*self.get_theme_value('edges-width'), height + 2*self.get_theme_value('edges-width'))

    def get_content_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def get_size(self) -> tuple[int, int]:
        return self.size

    def is_in_element(self, x: int, y: int) -> bool:
        return self.start_coords[0] <= x <= self.start_coords[0] + self.size[0] and self.start_coords[1] <= y <= self.start_coords[1] + self.size[1]

    def is_visible(self) -> bool:
        return self.visible
    
    def set_visibility(self, visible: bool) -> None:
        self.visible = visible
        self.ui_manager.ask_refresh()

    def display_element(self) -> bool:
        """
        Check whether the element can be displayed before calling the display method
        """
        if self.visible:
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
        self.hovered = False
        self.clicked = False
        self.unclicked = False
        
    def get_theme_value(self, variable: str) -> Any|None:
        return self.theme.get(variable)

    def display_edge(self) -> None:
        pygame.draw.rect(
            self.ui_manager.window,
            self.get_theme_value('edges-color'),
            pygame.Rect(
                self.start_coords[0],
                self.start_coords[1],
                self.size[0],
                self.size[1]
            ),
            self.get_theme_value('edges-width'),
            self.get_theme_value('border-radius'),
            self.get_theme_value('border-top-left-radius'),
            self.get_theme_value('border-top-right-radius'),
            self.get_theme_value('border-bottom-left-radius'),
            self.get_theme_value('border-bottom-right-radius')
        )