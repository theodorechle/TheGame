from ui_manager_interface import UIManagerInterface
from ui_element import UIElement
import pygame

class Slider(UIElement):
    DEFAULT_STEP_SIZE: int = 5 # in pixels
    DEFAULT_HEIGHT: int = 10
    def __init__(
            self,
            ui_manager: UIManagerInterface,
            min_value: int,
            max_value: int,
            step: int|float|None=None,
            round_precision: int|None=None,
            x: int|str=0,
            y: int|str=0,
            width: int|str|None=None,
            height: int|str|None=None,
            anchor: str = 'top-left',
            visible: bool = True,
            parent: UIElement | None = None,
            theme_elements_name: list[str] | None = None,
            classes_names: list[str]|None=None,
            background_image: str|pygame.Surface|None=None) -> None:
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self._value:int|float = self.min_value
        self.round_precision = round_precision
        self.cursor_radius = self.DEFAULT_HEIGHT
        if theme_elements_name is None:
            theme_elements_name = []
        theme_elements_name.append('slider')
        super().__init__(
            ui_manager,
            x,
            y,
            width,
            height,
            anchor,
            visible,
            parent,
            theme_elements_name,
            classes_names,
            background_image
        )
        self.can_have_focus = True
        self.value_x = 0

    def get_value(self) -> int|float:
        return self._value

    def set_value(self, value: int|float) -> None:
        value = max(min(self.max_value, value), self.min_value)
        self._value = value
        size_step = (self._size[0] - self.cursor_radius * 2) / ((self.max_value - self.min_value) / self.step)
        self.value_x = (value - self.min_value) / self.step * size_step
        self._ui_manager.ask_refresh(self)

    def get_content_size(self) -> tuple[int, int]:
        nb_values = self.max_value - self.min_value
        if self._relative_width:
            length = self.DEFAULT_STEP_SIZE*nb_values + self.cursor_radius
        else:
            length = self._size[0]
        if self._relative_height:
            height = self.DEFAULT_HEIGHT + self.cursor_radius
        else:
            height = self._size[1]
            self.cursor_radius = height//2
        return (length, height)
    
    def update(self) -> None:
        super().update()
        if self._clicked:
            self.set_value_with_mouse_pos()

    def set_value_with_mouse_pos(self) -> None:
        x = pygame.mouse.get_pos()[0]
        x -= self._start_coords[0]
        x -= self.cursor_radius
        x = min(self._size[0] - self.cursor_radius * 2, max(0, x))
        self.value_x = x
        if self.step:
            size_step = (self._size[0] - self.cursor_radius * 2) / ((self.max_value - self.min_value) / self.step)
            x /= size_step
            if isinstance(self.step, int):
                x = round(x)
            x *= self.step
            x += self.min_value
        else:
            x = 100 * x / self._size[0]
        if self.round_precision is not None:
            x = round(x, self.round_precision)
        self._value = x
        self._ui_manager.ask_refresh(self)

    def _display(self) -> None:
        super()._display()
        self.display_bar()
        self.display_cursor()
    
    def display_bar(self) -> None:
        pygame.draw.rect(
            self._ui_manager.get_window(),
            self.get_theme_value('bar-color'),
            pygame.Rect(
                self._start_coords[0] + self.cursor_radius // 2,
                self._start_coords[1] + self.cursor_radius // 2,
                self._size[0] - self.cursor_radius,
                self._size[1] - self.cursor_radius
            ),
            self.get_theme_value('border-radius'),
            self.get_theme_value('border-top-left-radius'),
            self.get_theme_value('border-top-right-radius'),
            self.get_theme_value('border-bottom-left-radius'),
            self.get_theme_value('border-bottom-right-radius')
        )
    
    def display_cursor(self) -> None:
        pygame.draw.circle(
            self._ui_manager.get_window(),
            self.get_theme_value('cursor-color'),
            (self.value_x + self._start_coords[0] + self.cursor_radius, self._start_coords[1] + self.cursor_radius),
            self.cursor_radius
        )

    def __copy__(self) -> "Slider":
        return Slider(self._ui_manager, self.min_value, self.max_value, self.step, self.round_precision, *self._first_coords, *self._first_size, self.anchor, self._visible, None, self.theme_elements_name, self.classes_names, self.background_image)
