import pygame
import items
from time import monotonic
from gui.elements import Table, Label
from gui.ui_element import UIElement
from gui.ui_manager import UIManager
from typing import Any
from math import ceil

class Inventory:
    def __init__(self, nb_cells: int, ui_manager: UIManager, cells: list[tuple[items.Item|None, int]]|None=None, gui_table_params: dict[str, Any]|None=None) -> None:
        self._nb_cells = nb_cells
        if cells:
            self.cells: list[tuple[items.Item|None, int]] = cells.copy()
        else:
            self.cells: list[tuple[items.Item|None, int]] = [(items.NOTHING, 0) for _ in range(self._nb_cells)] # list of list with items and quantities
        self._ui_manager = ui_manager
        self.cell_size = 40
        self.nb_cells_by_line = 10
        self.blocks_qty_font_name = ""
        self.blocks_qty_font_size = 20
        self.block_qty_font = pygame.font.SysFont(self.blocks_qty_font_name, self.blocks_qty_font_size)
        self._selected = 0
        self._is_opened = False
        # item, quantity
        self._current_clicked_item: tuple[items.Item|None, int] = (items.NOTHING, 0)
        self._clicked_item_init_pos = -1
        self._last_time_clicked = 0
        self._last_time_toggled = 0
        self.time_before_toggle = 0.2
        self.time_before_click = 0.2
        if gui_table_params is None:
            gui_table_params = {}
        self.inventory_table = Table(self._ui_manager, self.nb_cells_by_line, ceil(self._nb_cells / self.nb_cells_by_line), self.cell_size, self.cell_size, cells_classes_names=['inventory-cell'], **gui_table_params, visible=self._is_opened)
        for index, cell in enumerate(self.cells):
            element = self.inventory_table.add_element(index % self.nb_cells_by_line, index // self.nb_cells_by_line)
            element_child = element.add_element(UIElement(self._ui_manager, width="80%", height="80%", anchor="center"))
            if cell[0] is None: continue
            element_child.set_background_image(cell[0].image)
            element.add_element(Label(self._ui_manager, str(cell[1]), anchor="bottom-right", x="-4%", y="-2%", classes_names=['inventory-cell-label']))

    def update_cell_display_element(self, index: int) -> None:
        if index >= self.nb_cells_by_line: return
        cell = self.cells[index]
        if cell[0] is None: return
        element = self.inventory_table.get_element(index % self.nb_cells_by_line, index // self.nb_cells_by_line)
        element.set_background_image(cell[0].image)
        # change to have a better way to do this
        # maybe get with class name
        element._elements[1].set_text(str(cell[1]))
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
        self._ui_manager.display(False)

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

    def clicked_item(self) -> bool:
        """Return whether an item was clicked"""
        return self._clicked_item_init_pos != -1

    def get_clicked_cell(self, x: int, y: int) -> int:
        """
        Take the position of the mouse
        and return the index of the clicked cell in the inventory if clicked, else -1
        """
        return -1
        if self._last_time_clicked > monotonic() - self.time_before_click: return -1
        if self.main_bar_start_pos[1] <= y <= self.main_bar_start_pos[1] + self.cell_size: # main bar
            if self.main_bar_start_pos[0] <= x <= self.main_bar_start_pos[0] + self.cell_size * 10:
                x -= self.main_bar_start_pos[0]
                x //= self.cell_size
                index = x
            else: return -1
        elif self._is_opened and self.complete_inventory_start_pos[1] <= y <= self.complete_inventory_start_pos[1] + self.cell_size * (self._nb_cells // self.nb_cells_by_line + 1): # all inventory
            if self.complete_inventory_start_pos[0] <= x <= self.complete_inventory_start_pos[0] + self.cell_size * self.nb_cells_by_line:
                x -= self.complete_inventory_start_pos[0]
                x //= self.cell_size
                y -= self.complete_inventory_start_pos[1]
                y //= self.cell_size
                y += 1
                index = y * self.nb_cells_by_line + x
            else: return -1
        else:
            return -1
        if index >= self._nb_cells: return -1
        return index

    def click_cell(self, x: int, y: int) -> bool:
        index = self.get_clicked_cell(x, y)
        if index == -1: return False
        if self._current_clicked_item[0] is None:
            item, qty = self.empty_cell(index)
            if item is not items.NOTHING:
                self._clicked_item_init_pos = index
                self._current_clicked_item = (item, qty)
        else:
            self.place_clicked_item(index)
        self._last_time_clicked = monotonic()
        return True

    def place_clicked_item(self, pos: int) -> None:
        removed_qty = self.add_element_at_pos(self._current_clicked_item[0], self._current_clicked_item[1], pos)
        self._current_clicked_item = (self._current_clicked_item[0], self._current_clicked_item[1] - removed_qty)
        if self._current_clicked_item[1] == 0:
            self._current_clicked_item = (items.NOTHING, 0)
            self._clicked_item_init_pos = -1

    def place_back_clicked_item(self) -> None:
        self.place_clicked_item(self._clicked_item_init_pos)
        if self._clicked_item_init_pos == -1: return
        removed_qty = self.add_element(*self._current_clicked_item)
        self._current_clicked_item = (self._current_clicked_item[0], self._current_clicked_item[1] - removed_qty)
        if self._current_clicked_item[1] == 0:
            self._current_clicked_item = (items.NOTHING, 0)
            self._clicked_item_init_pos = -1

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