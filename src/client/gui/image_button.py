from button import Button
from ui_manager_interface import UIManagerInterface
from ui_element import UIElement
from typing import Callable
from pygame import Surface

class ImageButton(Button):
    """
    A button containing an image.
    """
    def __init__(self, ui_manager: UIManagerInterface, image: str|Surface, on_click_function: Callable[[Button], None] | None = None, x: int | str = 0, y: int | str = 0, width: int | str | None = None, height: int | str | None = None, anchor: str = 'top-left', visible: bool = True, parent: UIElement | None = None, theme_elements_name: list[str] | None = None, classes_names: list[str] | None = None, childs_classes_names: list[str]|None=None) -> None:
        if theme_elements_name is None:
            theme_elements_name = []
        theme_elements_name.append('image-button')
        super().__init__(ui_manager, on_click_function, x, y, width, height, anchor, visible, parent, theme_elements_name, classes_names, childs_classes_names, background_image=image)
    