from ui_element import UIElement
from ui_manager_interface import UIManagerInterface
from button import Button
from typing import Callable
from pygame import Surface
from typing import Any

class Table(UIElement):
    _SIZE_SCROLL_SHIFT = 10
    def __init__(
            self,
            ui_manager: UIManagerInterface,
            nb_elements_width: int,
            nb_elements_height: int,
            elements_width: int|None=None,
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
            cells_classes_names: list[str]|None=None,
            cells_childs_classes_names: list[str]|None=None,
            on_select_item_function: Callable[[Button], None]|None=None,
            background_image: str|Surface|None=None) -> None:
        if theme_elements_name is None:
            theme_elements_name = []
        self.scroll_shift = (0, 0)
        theme_elements_name.append('item-list')
        self.nb_elements_width = nb_elements_width
        self.nb_elements_height = nb_elements_height
        self.elements_width = elements_width
        self.elements_height = elements_height
        self._elements: list[Button] = [None for _ in range(self.nb_elements_width * self.nb_elements_height)]
        self.max_elements_heights = [self.elements_height] * self.nb_elements_height
        self.max_elements_widths = [self.elements_width] * self.nb_elements_width
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
        self.child_selected: Button|None = None
        self.cells_classes_names = [] if cells_classes_names is None else cells_classes_names
        self.cells_childs_classes_names = [] if cells_childs_classes_names is None else cells_childs_classes_names
        self.on_select_function = on_select_item_function
        
    def update_theme(self, theme_dict: dict[str, dict[str, Any]], erase: bool = False) -> None:
        super().update_theme(theme_dict, erase)
        for element in self._elements:
            if element is not None:
                element.update_theme(theme_dict, erase)
    
    def add_element(self, x: int, y: int) -> Button|None:
        index = x + y * self.nb_elements_width
        if index < 0 or index > len(self._elements): return
        previous_width = sum(self.max_elements_widths[:x])
        previous_height = sum(self.max_elements_heights[:y])
        new_element = Button(
            self._ui_manager,
            on_click_function=self.set_selected_child,
            x=previous_width,
            y=previous_height,
            width=self.elements_width,
            height=self.elements_height,
            classes_names=self.cells_classes_names.copy(),
            childs_classes_names=self.cells_childs_classes_names,
            parent=self,
            visible=self._visible
        )
        self._elements[index] = new_element
        new_element._can_have_focus = True
        self._ui_manager.ask_refresh()
        self.update_element()
        return new_element
    
    def remove_element(self, x: int, y: int) -> bool:
        index = x + y * self.nb_elements_width
        if index < 0 or index > len(self._elements): return False
        element = self._elements[index]
        if element is None: return False
        for class_name in self.cells_classes_names:
            try:
                element.classes_names.remove(class_name)
            except ValueError:
                pass
        element.parent = None
        self._elements[index] = None
        if self.child_selected == element:
            self.child_selected = None
        element.delete()
        self.update_element()
        self._ui_manager.ask_refresh()
        return True

    def get_element_by_index(self, index: int) -> Button|None:
        if index < 0 or index > len(self._elements): return None
        return self._elements[index]
    
    def get_element(self, x: int, y: int) -> Button|None:
        return self.get_element_by_index(x + y * self.nb_elements_width)

    def get_element_pos(self, element: UIElement) -> tuple[int, int]:
        """
        Returns a tuple (x, y) of the pos of the given element if in the table else (-1, -1)
        """
        for index, e in enumerate(self._elements):
            if e == element:
                return index % self.nb_elements_width, index // self.nb_elements_width
        return -1, -1

    def set_selected_child(self, element: UIElement) -> None:
        if self.child_selected is not None:
            self.child_selected.set_selected(False)
        self.child_selected = element
        self.child_selected.set_selected(True)
        if self.on_select_function is not None:
            self.on_select_function(self.child_selected)

    def get_selected_element(self) -> UIElement|None:
        return self.child_selected

    def get_content_size(self) -> tuple[int, int]:
        width = sum(self.max_elements_widths)
        height = sum(self.max_elements_heights)
        if not self._relative_width:
            width = min(self._size[0], width)
        if not self._relative_height:
            height = min(self._size[1], height)
        return width, height

    def update_element(self) -> None:
        self.max_elements_widths = [self.elements_width if self.elements_width is not None else 0 for _ in self.max_elements_widths]
        self.max_elements_heights = [self.elements_height if self.elements_height is not None else 0 for _ in self.max_elements_heights]
        for index, element in enumerate(self._elements):
            if element is None: continue
            x = index % self.nb_elements_width
            y = index // self.nb_elements_width
            self.max_elements_widths[x] = max(self.max_elements_widths[x], element._size[0])
            self.max_elements_heights[y] = max(self.max_elements_heights[y], element._size[1])
        super().update_element()
        for index, element in enumerate(self._elements):
            if element is None: continue
            x, y = index % self.nb_elements_width, index // self.nb_elements_width
            element._first_coords = (sum(self.max_elements_widths[:x]) - self._SIZE_SCROLL_SHIFT * self.scroll_shift[0], sum(self.max_elements_heights[:y]) - self._SIZE_SCROLL_SHIFT * self.scroll_shift[1])
            element._first_size = self.max_elements_widths[x], self.max_elements_heights[y]
            element.update_element()
    
    def scroll_elements(self) -> None:
        y = self.wheel_move[1]
        if y >= 0:
            y = min(y, self.scroll_shift[1])
        elif y < 0:
            if self._size[1] >= sum(self.max_elements_heights) - self.scroll_shift[1] * self._SIZE_SCROLL_SHIFT:
                y = 0
        x = self.wheel_move[0]
        if x >= 0:
            x = min(x, self.scroll_shift[0])
        elif x < 0:
            if self._size[0] >= sum(self.max_elements_widths) - self.scroll_shift[0] * self._SIZE_SCROLL_SHIFT:
                x = 0
        if x == 0 and y == 0: return
        self.scroll_shift = self.scroll_shift[0] - x, self.scroll_shift[1] - y
        for element in self._elements:
            if element is None: continue
        self.update_element()
        self._ui_manager.ask_refresh()

    def update(self) -> None:
        if self.wheel_move[0] != 0 or self.wheel_move[1] != 0:
            self.scroll_elements()
        super().update()

    def _display(self) -> None:
        super()._display()
        for element in self._elements:
            if element is None: continue
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

    def __copy__(self) -> "Table":
        copy = Table(self._ui_manager, self.nb_elements_width, self.nb_elements_height, self.elements_width, self.nb_elements_height, *self._first_coords, *self._first_size, self.anchor, self._visible, None, self.theme_elements_name, self.classes_names, self.background_image)
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