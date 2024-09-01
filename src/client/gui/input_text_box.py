from ui_element import UIElement
from ui_manager_interface import UIManagerInterface
from label import Label

import pygame

class InputTextBox(Label):
    def __init__(
            self,
            ui_manager: UIManagerInterface,
            text: str="",
            placeholder_text: str="",
            forbidden_chars: list[str]|None=None,
            allowed_chars: list[str]|None=None,
            loose_focus_on_enter: bool=False,
            x: int|str=0,
            y: int|str=0,
            width: int|str|None=None,
            height: int|str|None=None,
            min_width: int=0,
            min_height: int=0,
            anchor: str='top-left',
            visible: bool=True,
            parent: UIElement|None=None,
            theme_elements_name: list[str]|None=None,
            classes_names: list[str]|None=None,
            background_image: str|pygame.Surface|None=None) -> None:
        """
        A text box made for input usage.
        """
        if forbidden_chars is not None and allowed_chars is not None:
            raise ValueError("Can't set both forbidden and allowed chars")
        self.forbidden_chars = forbidden_chars
        self.allowed_chars = allowed_chars
        if theme_elements_name is None:
            theme_elements_name = []
        theme_elements_name.append('input-text-box')
        self._placeholder_text = placeholder_text
        self.loose_focus_on_enter = loose_focus_on_enter
        self._min_width = min_width
        self._min_height = min_height
        # the caret is the little be who is displayed when you write text
        self._caret_width = 1
        self._caret_x = len(text)
        self.is_placeholder_displayed = False
        self.text_displacement = 0
        self.show_caret = False
        super().__init__(
            ui_manager,
            text,
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
        self._can_have_focus = True
        self.was_focused = False
        if self.parent is not None:
            self.parent.update_element()
    
    def update(self) -> None:
        if self.was_focused and self._unclicked:
            self.set_caret_to_pos()
        if self._focus and not self.was_focused:
            self.was_focused = True
            pygame.key.start_text_input()
            pygame.key.set_text_input_rect(pygame.Rect(self.get_start_coords(), self.get_size()))
            self.set_caret_to_pos()
        if not self._focus and self.was_focused:
            pygame.key.stop_text_input()
            self.was_focused = False
            self.show_caret = False
            self._ui_manager.ask_refresh(self)
        return super().update()
    
    def update_size(self) -> None:
        width, height = self._size
        if self._relative_width or self._relative_height:
            content_width, content_height = self.get_content_size()
            content_width += 2*self._border_width
            content_height += 2*self._border_width
        if self._relative_width:
            width = content_width
            width += self._caret_width + 2
        if self._relative_height:
            height = content_height
        if width < self._min_width:
            width = self._min_width
        if height < self._min_height:
            height = self._min_height
        self._size = (width, height)

    def update_element(self) -> None:
        if not self._text:
            self._text = self._placeholder_text
            self.is_placeholder_displayed = True
        super().update_element()

    def process_event(self, event: pygame.event.Event) -> None:
        modified = False
        if event.type == pygame.TEXTINPUT:
            text = ''
            for char in event.text:
                if (self.forbidden_chars is None or char not in self.forbidden_chars) and (self.allowed_chars is None or char in self.allowed_chars):
                    text += char
            if self.is_placeholder_displayed:
                self.is_placeholder_displayed = False
                self._text = ""
            self._text = self._text[:self._caret_x] + text + self._text[self._caret_x:]
            self._caret_x += len(text)
            modified = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if not self.is_placeholder_displayed and self._caret_x > 0:
                    self._text = self._text[:self._caret_x - 1] + self._text[self._caret_x:]
                    self._caret_x -= 1
                    modified = True
            elif event.key == pygame.K_DELETE:
                if not self.is_placeholder_displayed and self._caret_x < len(self._text):
                    self._text = self._text[:self._caret_x] + self._text[self._caret_x + 1:]
                    modified = True
            elif event.key == pygame.K_RETURN:
                if self.loose_focus_on_enter:
                    self._ui_manager.set_focus(None)
            elif event.key == pygame.K_LEFT:
                if self._caret_x > 0:
                    self._caret_x -= 1
                    modified = True
            elif event.key == pygame.K_RIGHT:
                if self._caret_x < len(self._text) and not self.is_placeholder_displayed:
                    self._caret_x += 1
                    modified = True
        if modified:
            self.update_element()
            if self.parent is not None:
                self.parent.update_element()
            self._ui_manager.ask_refresh()
    
    def set_caret_to_pos(self) -> None:
        self.show_caret = True
        if self.is_placeholder_displayed:
            self._caret_x = 0
            self._ui_manager.ask_refresh(self)
            return
        px = pygame.mouse.get_pos()[0]
        px -= self._start_coords[0] - self._border_width
        for i in range(len(self._fit_text)):
            if self._font.size(self._fit_text[:i + 1])[0] > px:
                self._caret_x = self.text_displacement + i
                break
        self._ui_manager.ask_refresh(self)

    def get_caret_pos(self) -> None:
        return self._border_width + self._font.size(self._text[self.text_displacement:self._caret_x])[0] + 1

    def display_text(self) -> None:
        text_color = None
        if self._clicked:
            text_color = self.get_theme_value('clicked-text-color')
        elif self._hovered:
            text_color = self.get_theme_value('hovered-text-color')
        if text_color is None:
            if self.is_placeholder_displayed:
                text_color = self.get_theme_value('placeholder-color')
            else:
                text_color = self.get_theme_value('text-color')
        self._ui_manager.get_window().blit(self._font
            .render(self._fit_text, self.get_theme_value('antialias'), text_color), (self._start_coords[0] + self._border_width, self._start_coords[1] + self._border_width))

    def display_caret(self) -> None:
        x1, y1 = self.get_start_coords()
        x1 += self.get_caret_pos()
        y2 = y1 + self.get_size()[1] - self._border_width - 2
        y1 += self._border_width + 1
        pygame.draw.line(self._ui_manager.window, self.get_theme_value('caret-color'), (x1, y1), (x1, y2))

    def _display(self) -> None:
        super()._display()
        if self.show_caret:
            self.display_caret()
    
    def update_fit_text(self) -> None:
        """
        Set in 'self._fit_text' the text who can be entirely displayed with the actual size
        """
        if not self.is_placeholder_displayed and not self._relative_width:
            while self.get_caret_pos() > self.get_size()[0] - self._border_width:
                self.text_displacement += 1
            while self._caret_x < self.text_displacement:
                self.text_displacement -= 1
        text = self._text[self.text_displacement:]
        if not text:
            self._fit_text = ''
            return
        if self._relative_width:
            self._fit_text = text
        else:
            element_width = self._size[0]
            width = 0
            self._fit_text = ''
            for char in text:
                width = self._font.size(self._fit_text + char)[0]
                if width > element_width:
                    break
                self._fit_text += char
        if not self._relative_height:
            if self._font.size(self._fit_text)[1] + 2*self._border_width > self._size[1]:
                self._fit_text = ''
    
    def get_text(self) -> str:
        if self.is_placeholder_displayed:
            return ''
        return self._text

    def __copy__(self) -> "InputTextBox":
        return InputTextBox(self._ui_manager, self._text, self._placeholder_text, self.forbidden_chars, self.allowed_chars, self.loose_focus_on_enter, *self._first_coords, *self._first_size, self.anchor, self._visible, None, self.theme_elements_name, self.classes_names, self.background_image)
