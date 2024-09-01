from button import Button
from ui_manager_interface import UIManagerInterface
from typing import Callable
from ui_element import UIElement
from label import Label

class TextButton(Button):
    """
    A button containing a label.
    Note:
        Since a button is a container, if you want to apply some theming on the text,
        you must use the ':child' indicator after the class or the element name in the theming file.
        Also, the parent element is drawed before its childs, so things like the border theme should be
        applied to its childs, because the borders of the childs will erase the parent's ones.
    """
    def __init__(self, ui_manager: UIManagerInterface, text: str, on_click_function: Callable[[Button], None] | None = None, x: int | str = 0, y: int | str = 0, width: int | str | None = None, height: int | str | None = None, anchor: str = 'top-left', visible: bool = True, parent: UIElement | None = None, theme_elements_name: list[str] | None = None, classes_names: list[str] | None = None, childs_classes_names: list[str]|None=None, background_image: str | None = None) -> None:
        if theme_elements_name is None:
            theme_elements_name = []
        theme_elements_name.append('text-button')
        super().__init__(ui_manager, on_click_function, x, y, width, height, anchor, visible, parent, theme_elements_name, classes_names, childs_classes_names, background_image)
        self.label = Label(self._ui_manager, text, parent=self)
        self.label.fill_parent_width = True
        self.label.fill_parent_height = True
        self.add_element(self.label)
        self.update_element()
    
    def get_text(self) -> str:
        return self.label.get_text()

    def set_text(self, text: str) -> None:
        self.label.set_text(text)
    
