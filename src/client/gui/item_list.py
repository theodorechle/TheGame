from ui_element import UIElement
from ui_manager_interface import UIManagerInterface
from text_button import TextButton
from typing import Callable
from pygame import Surface
from typing import Any

class ItemList(UIElement):
    _DEFAULT_ELEMENT_HEIGHT = 50
    _SIZE_SCROLL_SHIFT = 10
    
    def __init__(
            self,
            ui_manager: UIManagerInterface,
            elements_height: int|None=None,
            x: int | str = 0,
            y: int | str = 0,
            width: int | str | None = None,
            height: int | str | None = None,
            anchor: str = 'top-left',
            visible: bool = True,
            parent: UIElement | None = None,
            theme_elements_name: list[str] | None = None,
            classes_names: list[str] | None = None,
            items_classes_names: list[str]|None=None,
            items_childs_classes_names: list[str]|None=None,
            on_select_item_function: Callable[[TextButton], None]|None=None,
            background_image: str|Surface|None=None) -> None:
        if theme_elements_name is None:
            theme_elements_name = []
        theme_elements_name.append('item-list')
        self.elements_height = elements_height if elements_height is not None else self._DEFAULT_ELEMENT_HEIGHT
        self._elements: list[TextButton] = []
        self.scroll_shift = (0, 0)
        self.max_child_size = 0
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
        self.child_selected: TextButton|None = None
        self.items_classes_names = [] if items_classes_names is None else items_classes_names
        self.items_childs_classes_names = [] if items_childs_classes_names is None else items_childs_classes_names
        self.on_select_function = on_select_item_function
        
    def update_theme(self, theme_dict: dict[str, dict[str, Any]], erase: bool = False) -> None:
        super().update_theme(theme_dict, erase)
        for element in self._elements:
            element.update_theme(theme_dict, erase)
    
    def add_element(self, text: str) -> None:
        self._elements.append(TextButton(
            self._ui_manager,
            text,
            on_click_function=self.set_selected_child,
            y=len(self._elements) * self.elements_height,
            height=self.elements_height,
            classes_names=self.items_classes_names.copy(),
            childs_classes_names=self.items_childs_classes_names,
            parent=self,
            visible=self._visible
            )
        )
        self._elements[-1]._can_have_focus = True
        self._elements[-1].fill_parent_width = True
        self.max_child_size = max(self.max_child_size, self._elements[-1]._size[0])
        if self._relative_width:
            self._size = (self.max_child_size, self._size[1])
        self._ui_manager.ask_refresh()
        self.update_element()
    
    def add_elements(self, texts: list[str]) -> None:
        for text in texts:
            self._elements.append(TextButton(
                self._ui_manager,
                text,
                on_click_function=self.set_selected_child,
                y=len(self._elements) * self.elements_height,
                height=self.elements_height,
                classes_names=self.items_classes_names.copy(),
                childs_classes_names=self.items_childs_classes_names,
                parent=self,
                visible=self._visible
                )
            )
            self._elements[-1]._can_have_focus = True
            self._elements[-1].fill_parent_width = True
            self.max_child_size = max(self.max_child_size, self._elements[-1]._size[0])
            if self._relative_width:
                self._size = (self.max_child_size, self._size[1])
        self._ui_manager.ask_refresh()
        self.update_element()
    
    def remove_element(self, element: UIElement) -> None:
        index = self._elements.index(element)
        if element not in self._elements: return False
        for class_name in self.items_classes_names:
            try:
                element.classes_names.remove(class_name)
            except ValueError:
                pass
        element.parent = None
        if self.child_selected == element:
            self.child_selected = None
        element.delete()
        self._elements.remove(element)
        for i in range(index, len(self._elements)):
            self._elements[i]._first_coords = self._elements[i]._first_coords[0], self._elements[i]._first_coords[1] - self.elements_height
        self.update_element()


    def remove_all_elements(self) -> None:
        for element in self._elements:
            try:
                for class_name in self.items_classes_names:
                    try:
                        element.classes_names.remove(class_name)
                    except ValueError:
                        pass
                element.parent = None
                if self.child_selected == element:
                    self.child_selected = None
                element.delete()
            except ValueError:
                pass
        self._elements.clear()
        self.update_element()
        self._ui_manager.ask_refresh()

    def set_selected_child(self, element: UIElement) -> None:
        if self.child_selected is not None:
            self.child_selected.set_selected(False)
        self.child_selected = element
        self.child_selected.set_selected(True)
        if self.on_select_function is not None:
            self.on_select_function(self.child_selected)

    def get_focused_value(self) -> str|None:
        if self.child_selected is None:
            return
        return self.child_selected.get_text()

    def get_content_size(self) -> tuple[int, int]:
        width = self._size[0] - 2*self._border_width if self._size[0] is not None else self._DEFAULT_ELEMENT_LENGTH
        height = self.elements_height * len(self._elements)
        if height != 0:
            height -= 2*self._border_width
        if not self._relative_width:
            width = min(self._size[0], width)
        if not self._relative_height:
            height = min(self._size[1], height)
        
        return width, height

    def update_element(self) -> None:
        super().update_element()
        for element in self._elements:
            element._first_size = self.max_child_size, element._first_size[1]
            element._relative_width = False
            element.update_element()
    
    def _display(self) -> None:
        super()._display()
        for element in self._elements:
            element._display()
    
    def scroll_elements(self) -> None:
        y = self.wheel_move[1]
        if y >= 0:
            y = min(y, self.scroll_shift[1])
        if y <= 0:
            if self.fit_in_parent_rect[3] >= self.elements_height * len(self._elements) - self.scroll_shift[1] * self._SIZE_SCROLL_SHIFT:
                y = 0
        x = self.wheel_move[0]
        if x >= 0:
            x = min(x, self.scroll_shift[0])
        if x <= 0:
            if self._size[0] >= self.max_child_size - self.scroll_shift[0] * self._SIZE_SCROLL_SHIFT:
                x = 0
        if x == 0 and y == 0: return
        self.scroll_shift = self.scroll_shift[0] - x, self.scroll_shift[1] - y
        for element in self._elements:
            element._first_coords = (element._first_coords[0] + self._SIZE_SCROLL_SHIFT * x, element._first_coords[1] + self._SIZE_SCROLL_SHIFT * y)
        self.update_element()
        self._ui_manager.ask_refresh()

    def update(self) -> None:
        if self.wheel_move[0] != 0 or self.wheel_move[1] != 0:
            self.scroll_elements()
        super().update()

    def _display(self) -> None:
        super()._display()
        for element in self._elements:
            element._display()

    def set_visibility(self, visible: bool) -> None:
        super().set_visibility(visible)
        for element in self._elements:
            if element is None: continue
            element.set_visibility(visible)

    def toggle_visibility(self) -> bool:
        super().toggle_visibility()
        for element in self._elements:
            if element is None: continue
            element.set_visibility(self._visible)

    def __copy__(self) -> "ItemList":
        copy = ItemList(self._ui_manager, self.elements_height, *self._first_coords, *self._first_size, self.anchor, self._visible, None, self.theme_elements_name, self.classes_names, self.background_image)
        copy._elements = [element.__copy__() for element in self._elements]
        for element in copy._elements:
            element.parent = copy
        copy.update_element()
        return copy

    def delete(self) -> None:
        for element in self._elements:
            element.delete()
        self._elements.clear()
        super().delete()