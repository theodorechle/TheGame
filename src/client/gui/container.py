from typing import Any
from ui_element import UIElement
from ui_manager_interface import UIManagerInterface
from pygame import Surface

class Container(UIElement):
    def __init__(
            self,
            ui_manager: UIManagerInterface,
            x: int = 0,
            y: int = 0,
            width: int | None = None,
            height: int | None = None,
            anchor: str = 'top-left',
            visible: bool = True,
            parent: UIElement | None = None,
            theme_elements_name: list[str] | None = None,
            classes_names: list[str]|None=None,
            childs_classes_names: list[str]|None=None,
            background_image: str|Surface|None=None) -> None:

        self._elements: list[UIElement] = []
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
        """
        Childs elements can get a theme by using
        ':<parent-element-class>:child'
        or
        '<parent-element-name>:child'
        """
        self.childs_classes_names = [] if childs_classes_names is None else childs_classes_names
    
    def update_theme(self, theme_dict: dict[str, dict[str, Any]], erase: bool = False) -> None:
        super().update_theme(theme_dict, erase)
        for element in self._elements:
            element.update_theme(theme_dict, erase)

    def add_element(self, element: UIElement) -> UIElement:
        self._elements.append(element)
        element.classes_names.extend(self.childs_classes_names)
        element.parent = self
        element.set_visibility(self._visible)
        self._ui_manager.update_element_theme(element, True)
        self._ui_manager.ask_refresh()
        if self.parent is not None:
            self.parent.update_element()
        else:
            self.update_element()
        return element
    
    def remove_element(self, element: UIElement) -> None:
        try:
            for class_name in self.childs_classes_names:
                try:
                    element.classes_names.remove(class_name)
                except ValueError:
                    pass
            element.parent = None
            element.delete()
            self._elements.remove(element)
            self.update_element()
            self._ui_manager.ask_refresh()
        except ValueError:
            pass
    
    def clear_elements_list(self) -> None:
        for element in self._elements:
            element.delete()
        self._elements.clear()
        self.update_element()
        self._ui_manager.ask_refresh()

    def get_content_size(self) -> tuple[int, int]:
        max_width, max_height = 0, 0
        for element in self._elements:
            width, height = element.get_size()
            max_width = max(max_width, width)
            max_height = max(max_height, height)
        return (max_width, max_height)

    def update_element(self) -> None:
        super().update_element()
        for element in self._elements:
            element.update_element()
    
    def _display(self) -> None:
        super()._display()
        for element in self._elements:
            element._display()

    def set_selected(self, selected: bool) -> None:
        for child in self._elements:
            child.set_selected(selected)
        super().set_selected(selected)

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
    
    def __copy__(self) -> "Container":
        copy = Container(self._ui_manager, *self._first_coords, *self._first_size, self.anchor, self._visible, None, self.theme_elements_name, self.classes_names, self.background_image)
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