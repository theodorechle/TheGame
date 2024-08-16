import items
from time import monotonic
from gui.elements import Table, Label
from gui.ui_element import UIElement
from gui.ui_manager import UIManager
from math import ceil

class Inventory:
    def __init__(self, nb_cells: int, ui_manager: UIManager, cells: list[tuple[items.Item|None, int]]|None=None, classes_names: list[str]|None=None, anchor: str = 'top-left') -> None:
        self._is_opened = False
        self._nb_cells = nb_cells
        if cells:
            self.cells: list[tuple[items.Item|None, int]] = cells.copy()
        else:
            self.cells: list[tuple[items.Item|None, int]] = [(items.NOTHING, 0) for _ in range(self._nb_cells)] # list of list with items and quantities
        self._ui_manager = ui_manager
        self.nb_cells_by_line = 10
        # ui elements initialization
        self.cell_size = 40
        if classes_names is None:
            classes_names = []
        self.inventory_table = Table(
            self._ui_manager,
            self.nb_cells_by_line,
            ceil(self._nb_cells / self.nb_cells_by_line),
            self.cell_size,
            self.cell_size,
            cells_classes_names=classes_names+['inventory-cell'],
            anchor=anchor,
            visible=self._is_opened)
        # creating every cells
        for index, cell in enumerate(self.cells):
            element = self.inventory_table.add_element(index % self.nb_cells_by_line, index // self.nb_cells_by_line)
            element.clickable = False
            # the element with the item image
            element_child = element.add_element(UIElement(self._ui_manager, width="80%", height="80%", anchor="center"))
            element_child._can_have_focus = False
            text = str(cell[1])
            if text == '0':
                text = ''
            label = Label(self._ui_manager, text, anchor="bottom-right", x="-10%", y="-2%", classes_names=['inventory-cell-label'])
            label._can_have_focus = False
            element.add_element(label)
            if cell[0] is not None:
                element_child.set_background_image(cell[0].image)
        # item, quantity
        self._current_clicked_item: tuple[items.Item|None, int] = (items.NOTHING, 0)
        self._selected = -1
        # timers
        self._last_time_toggled = 0
        self.time_before_toggle = 0.2
    
    def update_cell_display_element(self, index: int) -> None:
        if index >= self._nb_cells: return
        cell = self.cells[index]
        element = self.inventory_table.get_element_by_index(index)
        if cell[0] is None:
            element._elements[0].set_background_image(None)
            element._elements[1].set_text('')
        else:
            element._elements[0].set_background_image(cell[0].image)
            # change to have a better way to do this
            # maybe get with class name
            element._elements[1].set_text(str(cell[1]))
        element.update_element()
        self._ui_manager.ask_refresh(element)

    def add_element_at_pos(self, element: items.Item, quantity: int, pos: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at pos.
        Returns the quantity effectively added.
        """
        if 0 > pos or pos >= len(self.cells): return 0
        if self.cells[pos][0] == items.NOTHING: self.cells[pos] = (element, 0)
        elif self.cells[pos][0] != element: return 0
        added_quantity = min(quantity, element.stack_size - self.cells[pos][1])
        self.cells[pos] = (element, self.cells[pos][1] + added_quantity)
        self.update_cell_display_element(pos)
        return added_quantity
    
    def add_element(self, element: items.Item, quantity: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at the first free space.
        Returns the quantity effectively added.
        """
        added_quantity: int = 0
        for index in range(len(self.cells)):
            added_quantity = self.add_element_at_pos(element, quantity - added_quantity, index)
            if quantity == added_quantity:
                break
        return added_quantity
    
    def remove_element_at_pos(self, quantity: int, pos: int) -> tuple[items.Item|None, int]:
        """
        Tries to remove the quantity of the element in the inventory at pos.
        Returns the quantity effectively removed.
        """
        if 0 > pos or pos >= len(self.cells): return (None, 0)
        removed_quantity = min(quantity, self.cells[pos][1])
        cell = (self.cells[pos][0], removed_quantity)
        self.cells[pos] = (self.cells[pos][0], self.cells[pos][1] - removed_quantity)
        if self.cells[pos][1] == 0:
            self.cells[pos] = (items.NOTHING, 0)
        self.update_cell_display_element(pos)
        return cell

    def remove_element(self, element: items.Item) -> int:
        """
        Remove all instances of element in the inventory.
        Returns the quantity effectively removed
        """
        removed_quantity: int = 0
        for index in range(len(self.cells)):
            if self.cells[index][0] == element:
                removed_quantity += self.cells[index][1]
                self.cells[index] = (items.NOTHING, 0)
        return removed_quantity

    def get_element_quantity(self, element: items.Item) -> int:
        quantity = 0
        for cell in self.cells:
            if cell[0] != element: continue
            quantity += cell[1]
        return quantity

    def is_present_in_quantity(self, element: items.Item, quantity: int) -> bool:
        """
        Check if the given quantity of the given element is present in the inventory
        """
        for cell in self.cells:
            if cell[0] != element: continue
            quantity -= min(quantity, cell[1])
            if quantity == 0: break
        return quantity == 0

    def remove_quantity(self, element: items.Item, quantity: int) -> int:
        """
        Returns the quantity effectively removed
        """
        removed_quantity = 0
        for index, cell in enumerate(self.cells):
            if cell[0] != element: continue
            removed_quantity += self.remove_element_at_pos(quantity - removed_quantity, index)[1]
            if quantity == removed_quantity: return removed_quantity
        return removed_quantity

    def empty_cell(self, pos: int) -> tuple[items.Item|None, int]:
        """
        Empty the inventory's cell at pos.
        Returns a tuple containing the item in the cell and the quantity of it.
        """
        if 0 > pos or pos >= len(self.cells): return (items.NOTHING, 0)
        cell = self.cells[pos]
        self.cells[pos] = (items.NOTHING, 0)
        self.update_cell_display_element(pos)
        return cell

    def sort(self) -> None:
        ...

    def display(self) -> None:
        self._ui_manager.ask_refresh(self.inventory_table)

    def toggle_inventory(self) -> bool:
        """
        Returns whether it needs a screen update or not
        """
        if self._last_time_toggled > monotonic() - self.time_before_toggle: return False
        self._is_opened = not self._is_opened 
        self._last_time_toggled = monotonic()
        self.inventory_table.set_visibility(self._is_opened)
        return True
    
    def is_opened(self) -> bool:
        return self._is_opened

    def get_clicked_cell(self) -> int:
        for index in range(self._nb_cells):
            if self.inventory_table.get_element_by_index(index)._clicked:
                return index
        return -1

    def set_selected_cell(self, x: int, y: int) -> None:
        self.inventory_table.set_selected_child(self.inventory_table.get_element(x, y))
        self._selected = x + y*self.nb_cells_by_line

    def get_selected_cell(self) -> UIElement|None:
        return self.inventory_table.get_selected_element()
    
    def get_selected_index(self) -> int:
        return self._selected

def inventory_cells_to_ints(cells: list[tuple[items.Item|None, int]]) -> list[tuple[int, int]]:
    return [(items.ITEMS_DICT[cell[0]], cell[1]) if cell[0] is not None else cell for cell in cells]

def ints_to_inventory_cells(ints: list[tuple[int, int]]) -> list[tuple[items.Item|None, int]]:
    return [(items.REVERSED_ITEMS_DICT[cell[0]], cell[1]) if cell[0] is not None else cell for cell in ints]