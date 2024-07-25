from gui.ui_element import UIElement
from gui.ui_manager import UIManager

from pygame import font
from typing import Callable, Any

class Button(UIElement):
    def __init__(self, ui_manager: UIManager, text: str="", on_click_function: Callable[[UIElement], None]|None=None, start_x: int|None=None, start_y: int|None=None, width: int|None=None, height: int|None=None, horizontal_center: bool=False, vertical_center: bool=False, visible: bool=True, parent: UIElement|None=None) -> None:
        """
        A button who display a text and who can be clicked.
        If 'on_click_function' is given, the function will be called on click.
        """
        self.text = text
        self.on_click_function = on_click_function
        self.font: font.SysFont|None = None

        UIElement.__init__(self, ui_manager, start_x, start_y, width, height, horizontal_center, vertical_center, visible, parent, ['button'])

        self.fit_text = self.text
    
    def update_element(self) -> None:
        self.update_font()
        self.update_fit_text()
        self.update_size()
        super().update_element()

    def update_font(self) -> None:
        self.font = font.SysFont(
            self.get_theme_value('font-name'),
            self.get_theme_value('font-size')
        )

    def update(self) -> None:
        if self.unclicked and self.on_click_function is not None:
            self.on_click_function(self)
        super().update()

    def update_fit_text(self) -> None:
        """
        Set in 'self.fit_text' the text who can be entirely displayed with the actual size
        """
        if self.relative_width:
            self.fit_text = self.text
        else:
            element_width = self.size[0] - self.get_theme_value('edges-width') * 2
            width = 0
            for i, char in enumerate(self.text, 1):
                width += self.font.size(char)[0]
                if width > element_width:
                    break
            self.fit_text = self.text[:i]
        if not self.relative_height:
            if self.font.size(self.fit_text)[1] > self.size[1]:
                self.fit_text = ''

    def get_text_size(self) -> tuple[int, int]:
        if self.font is None:
            return (0, 0)
        return self.font.size(self.fit_text)

    def display_text(self) -> None:
        self.ui_manager.window.blit(self.font
            .render(self.fit_text, True, "#ffffff"), (self.start_coords[0] + self.get_theme_value('edges-width'), self.start_coords[1] + self.get_theme_value('edges-width')))

    def get_content_size(self) -> tuple[int, int]:
        return self.get_text_size()

    def display(self) -> None:
        self.display_text()
        self.display_edge()