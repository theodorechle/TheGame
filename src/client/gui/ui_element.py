from ui_manager_interface import UIManagerInterface
import pygame
from ui_element_interface import UIElementInterface

from typing import Any

class UIElement(UIElementInterface):
    def __init__(
            self,
            ui_manager: UIManagerInterface,
            x: int|str=0,
            y: int|str=0,
            width: int|str|None=None,
            height: int|str|None=None,
            anchor: str='top-left',
            visible: bool=True,
            parent: "UIElement|None"=None,
            theme_elements_name: list[str]|None=None,
            classes_names: list[str]|None=None,
            background_image: str|pygame.Surface|None=None) -> None:
        """
        Params:
        - ui_manager: the manager where will be send events and who keeps informations like window size
        - x: the value who will be added to the x of the element, after the anchor will be set
        - y: the value who will be added to the y of the element, after the anchor will be set
        - width: if not None, set the element width, else set relative size to True for width
        - height: if not None, set the element height, else set relative size to True for height
        - anchor: a string telling where the element will be positioned in his parent.
            Possible anchors: top-left, top, top-right, left, center, right, bottom-left, bottom, bottom-right
            Default is top-left
        - visible: Whether the element should be displayed or not
        - theme_elements_name: a list of the themes' names of the subclasses
        - background_image: if provided, the element will try to set the image at the given path as background image, replacing the background color
        The background image can ether be a pygame.Surface or a string path to the image
        Note:
            x, y, width and height can be strings, in which case they will be considered as a percentage of the screen size.
            They must be valid integers, and can be followed by an optional '%'.
        """
        self.theme_elements_name: list[str] = ['ui-element'] # a list of the class name and all is subclasses to get the themes
        if theme_elements_name is not None:
            self.theme_elements_name.extend(theme_elements_name)
        self.parent = parent
        self._theme: dict[str, dict[str, Any]] = {}
        self._border_width: int = 0
        self._ui_manager: UIManagerInterface = ui_manager
        self._first_coords: tuple[int|str, int|str] = x, y
        self._start_coords: tuple[int|str, int|str] = x, y
        self._first_size = (width, height)
        if isinstance(width, str):
            width = self.get_relative_width(width)
        if isinstance(height, str):
            height = self.get_relative_height(height)
        self._size = (width, height)
        self._relative_width = width is None
        self._relative_height = height is None
        self.fit_in_parent_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.anchor = anchor
        self._visible = visible
        self._hovered = False
        self._clicked = False
        self._unclicked = False
        self.wheel_move = (0, 0)
        self._can_have_focus = False
        self._focus = False
        self._selected = False
        self.fill_parent_width = False # allow element to expand or shrink to fill in its parent
        self.fill_parent_height = False # allow element to expand or shrink to fill in its parent
        self.classes_names = ['default'] if classes_names is None else [class_name for class_name in classes_names if ':' not in class_name] # ':' is reserved for special uses
        self._ui_manager.add_element(self)
        self.background_image: pygame.Surface|None = None
        self.set_background_image(background_image)
        self.update_element()

    def set_background_image(self, background_image: str|pygame.Surface|None=None) -> None:
        if isinstance(background_image, str):
            try:
                self.background_image = pygame.image.load(background_image)
            except FileNotFoundError:
                pass
        elif isinstance(background_image, pygame.Surface|None):
            self.background_image = background_image
        self.scaled_background_image: pygame.Surface|None = None

    def _resize_background_image(self) -> None:
        if self.background_image is not None:
            width, height = self.get_size()
            self.scaled_background_image = pygame.transform.scale(self.background_image, (width - 2*self._border_width, height - 2*self._border_width))
        
    def update_element(self) -> None:
        self.update_size()
        self.update_start_coords()
        self.set_fit_in_parent_rect()
        self._resize_background_image()

    def update_theme(self, theme_dict: dict[str, dict[str, Any]], erase: bool=False) -> None:
        """If erase is False, only the changed and added values will be set"""
        if erase:
            self._theme.clear()
        for element_name in self.theme_elements_name:
            if element_name in theme_dict:
                self._theme.update(theme_dict[element_name])
        parent = self.parent
        while parent is not None:
            for parent_theme_name in parent.theme_elements_name:
                if f'{parent_theme_name}:child' in theme_dict:
                    self._theme.update(theme_dict[f'{parent_theme_name}:child'])
            for parent_class_name in parent.classes_names:
                if f':{parent_class_name}:child' in theme_dict:
                    self._theme.update(theme_dict[f':{parent_class_name}:child'])
            parent = parent.parent
        for name in self.classes_names:
            if f':{name}' in theme_dict:
                self._theme.update(theme_dict[f':{name}'])
        self._border_width = max(0, self.get_theme_value('border-width'))

    def get_start_coords(self) -> tuple[int, int]:
        return self._start_coords

    def get_surface_rect(self) -> pygame.Rect:
        return pygame.Rect(self._start_coords, self._size)

    def update_start_coords(self) -> None:
        x, y = 0, 0
        if self.parent is None:
            parent_rect = (0, 0, *self._ui_manager.get_window_size())
        else:
            parent_rect = self.parent.get_surface_rect()
        if self.anchor == 'top-left':
            x = parent_rect[0]
            y = parent_rect[1]
        elif self.anchor == 'top':
            x = parent_rect[0] + parent_rect[2] // 2 - self.get_size()[0] // 2
            y = parent_rect[1]
        elif self.anchor == 'top-right':
            x = parent_rect[0] + parent_rect[2] - self.get_size()[0]
            y = parent_rect[1]
        elif self.anchor == 'center':
            x = parent_rect[0] + parent_rect[2] // 2 - self.get_size()[0] // 2
            y = parent_rect[1] + parent_rect[3] // 2 - self.get_size()[1] // 2
        elif self.anchor == 'left':
            x = parent_rect[0]
            y = parent_rect[1] + parent_rect[3] // 2 - self.get_size()[1] // 2
        elif self.anchor == 'right':
            x = parent_rect[0] + parent_rect[2] - self.get_size()[0]
            y = parent_rect[1] + parent_rect[3] // 2 - self.get_size()[1] // 2
        elif self.anchor == 'bottom-left':
            x = parent_rect[0]
            y = parent_rect[1] + parent_rect[3] - self.get_size()[1]
        elif self.anchor == 'bottom':
            x = parent_rect[0] + parent_rect[2] // 2 - self.get_size()[0] // 2
            y = parent_rect[1] + parent_rect[3] - self.get_size()[1]
        elif self.anchor == 'bottom-right':
            x = parent_rect[0] + parent_rect[2] - self.get_size()[0]
            y = parent_rect[1] + parent_rect[3] - self.get_size()[1]

        add_x = self._first_coords[0]
        if isinstance(add_x, str):
            add_x = self.get_relative_width(add_x)
        x += add_x
        add_y = self._first_coords[1]
        if isinstance(add_y, str):
            add_y = self.get_relative_height(add_y)
        y += add_y
        if self.fill_parent_width:
            x = parent_rect[0]
        if self.fill_parent_height:
            y = parent_rect[1]
        self._start_coords = x, y
    
    def get_relative_width(self, width: str) -> int:
        if width[-1] == '%':
            width = width[:-1]
        if self.parent is not None:
            parent_size = self.parent.get_size()[0]
        else:
            parent_size = self._ui_manager.get_window_size()[0]
        return parent_size * int(width) // 100

    def get_relative_height(self, height: str) -> int:
        if height[-1] == '%':
            height = height[:-1]
        if self.parent is not None:
            parent_size = self.parent.get_size()[1]
        else:
            parent_size = self._ui_manager.get_window_size()[1]
        return parent_size * int(height) // 100

    def update_size(self) -> None:
        width, height = self._first_size
        if isinstance(width, str):
            width = self.get_relative_width(width)
        if isinstance(height, str):
            height = self.get_relative_height(height)
        if self._relative_width or self._relative_height:
            content_width, content_height = self.get_content_size()
        if self._relative_width:
            width = content_width
        if self._relative_height:
            height = content_height
        if self.fill_parent_width:
            width = self.parent._size[0]
        if self.fill_parent_height:
            height = self.parent._size[1]
        self._size = (width, height)

    def set_fit_in_parent_rect(self) -> pygame.Rect:
        start_x, start_y = self._start_coords
        length, height = self._size
        if self.parent is None:
            parent_x, parent_y, parent_length, parent_height = 0, 0, *self._ui_manager.get_window_size()
        else:
            parent_x, parent_y, parent_length, parent_height = self.parent.fit_in_parent_rect
        if start_x >= parent_x:
            length = max(min(length, parent_length - (start_x - parent_x)), 0)
        else:
            if length >= parent_length:
                length = max(min(length, parent_length), 0)
            else:
                length = max(length - (parent_x - start_x), 0)
        if start_y >= parent_y:
            height = max(min(height, parent_height - (start_y - parent_y)), 0)
        else:
            if height >= parent_height:
                height = max(min(height, parent_height), 0)
            else:
                height = max(height - (parent_y - start_y), 0)
        
        start_x = min(max(start_x, parent_x), parent_x + parent_length)
        start_y = min(max(start_y, parent_y), parent_y + parent_height)
        self.fit_in_parent_rect = pygame.Rect(start_x, start_y, length, height)

    def get_content_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def get_size(self) -> tuple[int, int]:
        return self._size

    def is_in_element(self, x: int, y: int) -> bool:
        return self.fit_in_parent_rect[0] <= x <= self.fit_in_parent_rect[0] + self.fit_in_parent_rect[2] and self.fit_in_parent_rect[1] <= y <= self.fit_in_parent_rect[1] + self.fit_in_parent_rect[3]

    def get_visibility(self) -> bool:
        return self._visible
    
    def set_visibility(self, visible: bool) -> None:
        self._visible = visible
        self._ui_manager.ask_refresh()
    
    def toggle_visibility(self) -> bool:
        """Returns True if visible else False"""
        self._visible = not self._visible
        self._ui_manager.ask_refresh()
        return self._visible

    def set_focus(self, focus: bool) -> bool:
        if self._can_have_focus:
            self._focus = focus
            if self._focus and self.get_theme_value('focused-border-color') is not None:
                self._ui_manager.ask_refresh(self)
        return self._focus

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        if self.get_theme_value('selected-border-color') is not None:
            self._ui_manager.ask_refresh(self)

    def set_clicked(self, clicked: bool) -> None:
        self._clicked = clicked
        if self.get_theme_value('clicked-border-color') is not None:
            self._ui_manager.ask_refresh(self)

    def set_unclicked(self, unclicked: bool) -> None:
        self._unclicked = unclicked
        if self.get_theme_value('unclicked-border-color') is not None:
            self._ui_manager.ask_refresh(self)

    def set_hovered(self, hovered: bool) -> None:
        self._hovered = hovered
        if self.get_theme_value('hovered-border-color') is not None:
            self._ui_manager.ask_refresh(self)

    def is_focusable(self) -> bool:
        return self._can_have_focus

    def display_element(self) -> None:
        """Check whether the element can be displayed before calling the display method"""
        if self._visible:
            self._display()
    
    def _display(self) -> None:
        """Should not be called directly by external programs but using display_element method"""
        self.display_borders()
    
    def update(self) -> None:
        """
        Should be called by the subclasses to update the values linked to an event
        (hovered, clicked, ...)
        """
        self.wheel_move = (0, 0)
        
    def get_theme_value(self, variable: str) -> Any|None:
        return self._theme.get(variable)

    def display_borders(self) -> None:
        border_color = None
        if self._hovered:
            border_color = self.get_theme_value('hovered-border-color')
        if border_color is None and self._clicked:
            border_color = self.get_theme_value('clicked-border-color')
        if border_color is None and self._selected:
            border_color = self.get_theme_value('selected-border-color')
        if border_color is None and self._focus:
            border_color = self.get_theme_value('focused-border-color')
        if border_color is None:
            border_color = self.get_theme_value('border-color')
        start_x, start_y, length, height = self.fit_in_parent_rect
        if self.scaled_background_image is not None:
            self._ui_manager.get_window().blit(self.scaled_background_image, (start_x + self._border_width, start_y + self._border_width, length - 2*self._border_width, height - 2*self._border_width))
        else:
            background_color = self.get_theme_value('background-color')
            if background_color is not None:
                self._ui_manager.get_window().fill(background_color, (start_x + self._border_width, start_y + self._border_width, length - 2*self._border_width, height - 2*self._border_width))
        pygame.draw.rect(
            self._ui_manager.get_window(),
            border_color,
            pygame.Rect(
                start_x,
                start_y,
                length,
                height
            ),
            self.get_theme_value('border-width'),
            self.get_theme_value('border-radius'),
            self.get_theme_value('border-top-left-radius'),
            self.get_theme_value('border-top-right-radius'),
            self.get_theme_value('border-bottom-left-radius'),
            self.get_theme_value('border-bottom-right-radius')
        )

    def process_event(self, event: pygame.event.Event) -> None:
        """
        If the element have the focus and the event can't be processed by the ui manager,
        the element will receive the events in order to process them.
        """
    
    def get_parent(self) -> UIElementInterface|None:
        return self.parent

    def __copy__(self) -> "UIElement":
        return UIElement(self._ui_manager, *self._first_coords, *self._first_size, self.anchor, self._visible, None, self.theme_elements_name, self.classes_names, self.background_image)

    def delete(self) -> None:
        """
        Delete all is known references
        """
        self._ui_manager.remove_element(self)