from typing import Any
from ui_element import UIElement
from ui_manager_interface import UIManagerInterface

from pygame import font, Surface

class Label(UIElement):
    def __init__(
            self,
            ui_manager: UIManagerInterface,
            text: str="",
            x: int|str=0,
            y: int|str=0,
            width: int|str|None=None,
            height: int|str|None=None,
            anchor: str='top-left',
            visible: bool=True,
            parent: UIElement|None=None,
            theme_elements_name: list[str]|None=None,
            classes_names: list[str]|None=None,
            background_image: str|Surface|None=None) -> None:
        """
        A simple way to display text.
        """
        self._text = text
        self._font: font.Font|None = None
        if theme_elements_name is None:
            theme_elements_name = []
        theme_elements_name.append('label')
        self._fit_text = self._text
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

        self.can_have_focus = False
    
    def update_theme(self, theme_dict: dict[str, Any], erase: bool=False) -> None:
        super().update_theme(theme_dict, erase)
        self.update_font()

    def update_element(self) -> None:
        self.update_fit_text()
        super().update_element()

    def update_font(self) -> None:
        self._font = font.SysFont(
            self.get_theme_value('font-name'),
            self.get_theme_value('font-size')
        )

    def update_fit_text(self) -> None:
        """
        Set in 'self._fit_text' the text who can be entirely displayed with the actual size
        """
        if not self._text:
            self._fit_text = ''
            return
        if self._relative_width:
            self._fit_text = self._text
        else:
            element_width = self._size[0]
            width = 0
            self._fit_text = ''
            for char in self._text:
                width = self._font.size(self._fit_text + char)[0]
                if width > element_width:
                    break
                self._fit_text += char
        if not self._relative_height:
            if self._font.size(self._fit_text)[1] > self._size[1]:
                self._fit_text = ''

    def get_text_size(self) -> tuple[int, int]:
        if self._font is None:
            return (0, 0)
        return self._font.size(self._fit_text)

    def display_text(self) -> None:
        text_color = None
        if self._hovered:
            text_color = self.get_theme_value('hovered-text-color')
        if text_color is None and self._clicked:
            text_color = self.get_theme_value('clicked-text-color')
        if text_color is None and self._selected:
            text_color = self.get_theme_value('selected-text-color')
        if text_color is None and self._focus:
            text_color = self.get_theme_value('focused-text-color')
        if text_color is None:
            text_color = self.get_theme_value('text-color')
        text_size = self.get_text_size()
        start_x, start_y = 0, 0
        if self.get_theme_value('horizontal-center'):
            start_x = self._size[0] // 2 - text_size[0] // 2
        if self.get_theme_value('vertical-center'):
            start_y = self._size[1] // 2 - text_size[1] // 2
        text = self._fit_text
        start_x += self._start_coords[0]
        start_y += self._start_coords[1]
        if self.parent is not None:
            if start_y < self.parent.fit_in_parent_rect[1] or start_y + text_size[1] > self.parent.fit_in_parent_rect[1] + self.parent.fit_in_parent_rect[3]:
                return
            while text and start_x < self.parent.fit_in_parent_rect[0]:
                char_length = self._font.size(text[0])[0]
                text = text[1:]
                start_x += char_length
                text_size = text_size[0] - char_length, text_size[1]
            while text and start_x + text_size[0] > self.parent.fit_in_parent_rect[0] + self.parent.fit_in_parent_rect[2]:
                text = text[:-1]
                text_size = self._font.size(text)

        text_rendered = self._font.render(text,
                            self.get_theme_value('antialias'),
                            text_color)
        transparency = self.get_theme_value('text-transparency')
        if transparency is not None:
            text_rendered.set_alpha(transparency)
        self._ui_manager.get_window().blit(text_rendered,
                    (start_x, start_y)
        )

    def get_content_size(self) -> tuple[int, int]:
        return self.get_text_size()

    def _display(self) -> None:
        super()._display()
        self.display_text()
    
    def set_text(self, text: str) -> None:
        self._text = text
        self.update_element()
        self._ui_manager.ask_refresh()
    
    def get_text(self) -> str:
        return self._text

    def update(self) -> None:
        super().update()
    
    def set_selected(self, selected: bool) -> None:
        super().set_selected(selected)
        if self.get_theme_value('selected-text-color') is not None:
            self._ui_manager.ask_refresh(self)

    def set_clicked(self, clicked: bool) -> None:
        super().set_clicked(clicked)
        if self.get_theme_value('clicked-text-color') is not None:
            self._ui_manager.ask_refresh(self)

    def set_unclicked(self, unclicked: bool) -> None:
        super().set_unclicked(unclicked)
        if self.get_theme_value('unclicked-text-color') is not None:
            self._ui_manager.ask_refresh(self)

    def set_hovered(self, hovered: bool) -> None:
        super().set_hovered(hovered)
        if self.get_theme_value('hovered-text-color') is not None:
            self._ui_manager.ask_refresh(self)

    def __copy__(self) -> "Label":
        return Label(self._ui_manager, self._text, *self._first_coords, *self._first_size, self.anchor, self._visible, None, self.theme_elements_name, self.classes_names, self.background_image)
